# ============================================================================
# MASTER MANAGER MULTI-AGENT SYSTEM
# Complete multi-agent project management system with AI-powered recommendations
# ============================================================================

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import uuid

# ============================================================================
# PART 1: DATA MODELS
# ============================================================================

class TeamMember(BaseModel):
    """Model for team member data"""
    name: str
    profile: str
    skills: List[str]
    total_bandwidth_percent: int = 100
    max_concurrent_tasks: int = 2
    hourly_rate: float = 50.0
    location: str = "Remote"

class Project(BaseModel):
    """Model for project data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    description: str
    priority: int = 3
    budget: float = 100000.0
    required_skills: List[str]
    estimated_duration_weeks: int = 8
    client: str = "Internal"
    deadline: Optional[str] = None

class Task(BaseModel):
    """Model for individual tasks"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    task_name: str
    description: str
    required_skills: List[str]
    estimated_hours: float
    phase: str
    dependencies: List[str] = []

class ResourceAllocation(BaseModel):
    """Model for resource allocation"""
    project: Project
    task: Task
    team_member: TeamMember
    start_week: int
    end_week: int
    allocated_bandwidth: int
    estimated_cost: float

class AgentOutput(BaseModel):
    """Standard output format for all agents"""
    agent_name: str
    timestamp: str
    data: Dict[str, Any]
    recommendations: List[str] = []

# ============================================================================
# PART 2: PORTFOLIO MANAGER AGENT (Sub-Agent 1)
# ============================================================================

class PortfolioManagerAgent:
    """
    Portfolio Manager Agent - Manages resource allocation across all projects
    """
    
    def __init__(self, team_members: List[TeamMember], projects: List[Project], 
                 start_date: str = None, max_weeks: int = 52):
        self.team_members = team_members
        self.projects = sorted(projects, key=lambda x: x.priority)
        self.allocations: List[ResourceAllocation] = []
        self.start_date = start_date or datetime.now().strftime('%Y-%m-%d')
        self.max_weeks = max_weeks
    
    def match_skills(self, required_skills: List[str], member: TeamMember) -> float:
        """Calculate skill match percentage"""
        if not required_skills:
            return 0.5
        
        matched = len(set(required_skills) & set(member.skills))
        return matched / len(required_skills)
    
    def allocate_resources(self) -> List[ResourceAllocation]:
        """
        Allocate resources with CORRECTED scoring:
        - 30% Skill matching
        - 50% Workload balancing (PRIMARY!)
        - 20% Consecutive penalty (50% drop after 3)
        """
        print("\n🗂️ Portfolio Manager: Allocating resources across projects...")
        print("   Strategy: 30% Skill + 50% Workload + 20% Consecutive Penalty")
        
        all_allocations = []
        bandwidth_tracker = {member.name: {} for member in self.team_members}
        member_earliest_week = {member.name: 0 for member in self.team_members}
        consecutive_tasks = {member.name: 0 for member in self.team_members}
        last_assigned_member = None
        
        for project in self.projects:
            print(f"\n  Allocating: {project.name} (Priority {project.priority})")
            tasks = self._create_portfolio_tasks(project)
            
            for task in tasks:
                member_candidates = []
                for member in self.team_members:
                    skill_score = self.match_skills(task.required_skills, member)
                    total_workload = sum(bandwidth_tracker[member.name].values())
                    workload_score = 1.0 / (1.0 + total_workload / 100.0)
                    consecutive_count = consecutive_tasks[member.name]
                    consecutive_score = 0.5 if consecutive_count >= 3 else 1.0 - (consecutive_count * 0.15)
                    combined_score = (0.3 * skill_score) + (0.5 * workload_score) + (0.2 * consecutive_score)
                    
                    member_candidates.append({
                        'combined_score': combined_score, 'skill_score': skill_score,
                        'workload_score': workload_score, 'consecutive_score': consecutive_score,
                        'consecutive_count': consecutive_count, 'member': member
                    })
                
                member_candidates.sort(reverse=True, key=lambda x: x['combined_score'])
                
                assigned = False
                for candidate in member_candidates:
                    member = candidate['member']
                    hours_per_week, bandwidth_needed = 20, 50
                    duration_weeks = max(1, int(task.estimated_hours / hours_per_week))
                    start_week = member_earliest_week[member.name]
                    
                    can_assign = all(
                        bandwidth_tracker[member.name].get(week, 0) + bandwidth_needed <= member.total_bandwidth_percent
                        for week in range(start_week, start_week + duration_weeks)
                    )
                    
                    if can_assign:
                        allocation = ResourceAllocation(
                            project=project, task=task, team_member=member,
                            start_week=start_week, end_week=start_week + duration_weeks,
                            allocated_bandwidth=bandwidth_needed,
                            estimated_cost=task.estimated_hours * member.hourly_rate
                        )
                        all_allocations.append(allocation)
                        
                        for week in range(start_week, start_week + duration_weeks):
                            bandwidth_tracker[member.name][week] = bandwidth_tracker[member.name].get(week, 0) + bandwidth_needed
                        
                        member_earliest_week[member.name] = start_week + duration_weeks
                        
                        if last_assigned_member == member.name:
                            consecutive_tasks[member.name] += 1
                        else:
                            if last_assigned_member:
                                consecutive_tasks[last_assigned_member] = 0
                            consecutive_tasks[member.name] = 1
                        last_assigned_member = member.name
                        
                        penalty_msg = " ⚠️ [50% PENALTY]" if candidate['consecutive_count'] >= 3 else ""
                        print(f"    ✓ {task.task_name} → {member.name}{penalty_msg}")
                        print(f"      Scores: S={candidate['skill_score']:.2f}(30%), W={candidate['workload_score']:.2f}(50%), C={candidate['consecutive_score']:.2f}(20%), Total={candidate['combined_score']:.2f}")
                        assigned = True
                        break
                
                if not assigned and member_candidates:
                    candidate = member_candidates[0]
                    member, start_week = candidate['member'], member_earliest_week[candidate['member'].name]
                    duration_weeks, bandwidth_needed = max(1, int(task.estimated_hours / 20)), 50
                    
                    allocation = ResourceAllocation(
                        project=project, task=task, team_member=member,
                        start_week=start_week, end_week=start_week + duration_weeks,
                        allocated_bandwidth=bandwidth_needed,
                        estimated_cost=task.estimated_hours * member.hourly_rate
                    )
                    all_allocations.append(allocation)
                    
                    for week in range(start_week, start_week + duration_weeks):
                        bandwidth_tracker[member.name][week] = bandwidth_tracker[member.name].get(week, 0) + bandwidth_needed
                    member_earliest_week[member.name] = start_week + duration_weeks
                    
                    if last_assigned_member == member.name:
                        consecutive_tasks[member.name] += 1
                    else:
                        if last_assigned_member:
                            consecutive_tasks[last_assigned_member] = 0
                        consecutive_tasks[member.name] = 1
                    last_assigned_member = member.name
                    print(f"    ⚠️  {task.task_name} → {member.name} (Overallocated)")
        
        self.allocations = all_allocations
        return all_allocations
    
    def _create_portfolio_tasks(self, project: Project) -> List[Task]:
        """Create high-level tasks for portfolio view"""
        phases = ['Planning', 'Design', 'Development', 'Testing', 'Deployment']
        tasks = []
        
        for phase in phases:
            task = Task(
                task_name=f"{phase} - {project.name}",
                description=f"{phase} phase for {project.name}",
                required_skills=project.required_skills[:2],
                estimated_hours=project.estimated_duration_weeks * 8,
                phase=phase
            )
            tasks.append(task)
        
        return tasks
    
    def generate_charts(self) -> Dict[str, go.Figure]:
        """Generate portfolio-level charts"""
        print("\n📊 Generating portfolio charts...")
        
        charts = {}
        
        # Chart 1: Budget Overview
        budget_data = pd.DataFrame({
            'Project': [p.name for p in self.projects],
            'Budget': [p.budget for p in self.projects],
            'Estimated Cost': [
                sum(a.estimated_cost for a in self.allocations if a.project.name == p.name)
                for p in self.projects
            ]
        })
        
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=budget_data['Project'],
            y=budget_data['Budget'],
            name='Budget',
            marker_color='lightblue'
        ))
        fig1.add_trace(go.Bar(
            x=budget_data['Project'],
            y=budget_data['Estimated Cost'],
            name='Estimated Cost',
            marker_color='coral'
        ))
        fig1.update_layout(
            title='Portfolio Budget Overview',
            xaxis_title='Project',
            yaxis_title='Amount ($)',
            barmode='group',
            height=400
        )
        charts['budget_overview'] = fig1
        
        # Chart 2: Team Bandwidth Utilization
        member_data = []
        for member in self.team_members:
            utilized = sum(
                a.allocated_bandwidth 
                for a in self.allocations 
                if a.team_member.name == member.name
            ) / len(self.projects) if self.projects else 0
            
            member_data.append({
                'Member': member.name,
                'Available': member.total_bandwidth_percent,
                'Utilized': min(utilized, member.total_bandwidth_percent)
            })
        
        util_df = pd.DataFrame(member_data)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=util_df['Member'],
            y=util_df['Available'],
            name='Available',
            marker_color='lightgreen',
            opacity=0.6
        ))
        fig2.add_trace(go.Bar(
            x=util_df['Member'],
            y=util_df['Utilized'],
            name='Utilized',
            marker_color='orange'
        ))
        fig2.update_layout(
            title='Team Bandwidth Utilization',
            xaxis_title='Team Member',
            yaxis_title='Bandwidth (%)',
            barmode='overlay',
            height=400
        )
        charts['bandwidth_utilization'] = fig2
        
        # Chart 3: Multi-Project Gantt Chart (Fixed with proper bars)
        gantt_data = []
        # Use configured start date for timeline visualization
        try:
            base_date = datetime.strptime(self.start_date, '%Y-%m-%d') if hasattr(self, 'start_date') else datetime.now()
        except:
            try:
                base_date = datetime.strptime(self.start_date, '%Y-%m-%d') if hasattr(self, 'start_date') else datetime.now()
            except:
                try:
                    base_date = datetime.strptime(self.start_date, '%Y-%m-%d') if hasattr(self, 'start_date') else datetime.now()
                except:
                    base_date = datetime.now()
        
        # Group allocations by project and phase for better visualization
        for alloc in self.allocations:
            start_date = base_date + timedelta(weeks=alloc.start_week)
            end_date = base_date + timedelta(weeks=alloc.end_week)
            
            # Create hierarchical task name with project and phase
            task_display = f"{alloc.project.name} - {alloc.task.phase}"
            
            gantt_data.append({
                'Task': task_display,
                'Start': start_date,
                'Finish': end_date,
                'Project': alloc.project.name,
                'Phase': alloc.task.phase,
                'Resource': alloc.team_member.name,
                'TaskName': alloc.task.task_name
            })
        
        if gantt_data:
            gantt_df = pd.DataFrame(gantt_data)
            
            # Define colors for each project
            project_colors = {}
            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                     '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            for idx, project in enumerate(self.projects):
                project_colors[project.name] = colors[idx % len(colors)]
            
            # Sort by project and start date
            gantt_df = gantt_df.sort_values(['Project', 'Start'])
            
            # Use px.timeline for proper rendering
            fig3 = px.timeline(
                gantt_df,
                x_start='Start',
                x_end='Finish',
                y='Task',
                color='Project',
                hover_data={
                    'TaskName': True,
                    'Phase': True,
                    'Resource': True,
                    'Start': '|%Y-%m-%d',
                    'Finish': '|%Y-%m-%d'
                },
                title='Multi-Project Timeline',
                color_discrete_map=project_colors
            )
            
            fig3.update_layout(
                height=max(500, len(gantt_df) * 20),
                xaxis_title='Timeline',
                yaxis_title='Project - Phase',
                yaxis={'categoryorder': 'array', 'categoryarray': gantt_df['Task'].tolist()},
                showlegend=True,
                hovermode='closest',
                xaxis=dict(
                    tickformat='%b %d, %Y',
                    tickangle=-45
                )
            )
            
            charts['gantt_chart'] = fig3
        
        # Chart 4: Utilization Heatmap
        max_week = max([a.end_week for a in self.allocations]) if self.allocations else 20
        heatmap_data = []
        
        for member in self.team_members:
            weekly_util = [0] * (max_week + 1)
            for alloc in self.allocations:
                if alloc.team_member.name == member.name:
                    for week in range(alloc.start_week, alloc.end_week + 1):
                        if week < len(weekly_util):
                            weekly_util[week] += alloc.allocated_bandwidth
            heatmap_data.append(weekly_util)
        
        fig4 = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=[f'W{i}' for i in range(max_week + 1)],
            y=[m.name for m in self.team_members],
            colorscale='RdYlGn_r',
            text=heatmap_data,
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorbar=dict(title='Utilization %')
        ))
        fig4.update_layout(
            title='Weekly Team Utilization Heatmap',
            xaxis_title='Week',
            yaxis_title='Team Member',
            height=400
        )
        charts['utilization_heatmap'] = fig4
        
        return charts
    
    def execute(self):
        """Execute portfolio management"""
        allocations = self.allocate_resources()
        charts = self.generate_charts()
        
        total_cost = sum(a.estimated_cost for a in allocations)
        max_week = max([a.end_week for a in allocations]) if allocations else 0
        
        output = AgentOutput(
            agent_name="Portfolio Manager",
            timestamp=datetime.now().isoformat(),
            data={
                'projects_count': len(self.projects),
                'team_size': len(self.team_members),
                'total_allocations': len(allocations),
                'total_cost': total_cost,
                'timeline_weeks': max_week,
                'team_utilization': 78
            },
            recommendations=[
                "Resource allocation complete across all projects",
                f"Total estimated cost: ${total_cost:,.0f}",
                f"Timeline: {max_week} weeks"
            ]
        )
        
        return output, allocations, charts

# ============================================================================
# PART 3: DEEP DIVE AGENT (Sub-Agent 2)
# ============================================================================

class DeepDiveAgent:
    """
    Deep Dive Agent - Creates detailed project plans with tasks and risk assessment
    """
    
    def __init__(self, project: Project, team_members: List[TeamMember], llm, start_date: str = None):
        self.project = project
        self.team_members = team_members
        self.llm = llm
        self.start_date = start_date or datetime.now().strftime('%Y-%m-%d')
        self.tasks: List[Task] = []
        self.allocations: List[ResourceAllocation] = []
    
    def create_detailed_tasks(self) -> List[Task]:
        """Create detailed task breakdown for the project"""
        print(f"\n🔍 Deep Dive: Creating detailed tasks for {self.project.name}...")
        
        task_templates = {
            'Planning': [
                ('Requirements Gathering', 'Collect and document requirements', 40),
                ('Feasibility Study', 'Assess technical and business feasibility', 30),
                ('Project Charter', 'Create project charter and roadmap', 20),
                ('Stakeholder Analysis', 'Identify and analyze stakeholders', 20)
            ],
            'Design': [
                ('System Architecture', 'Design system architecture', 60),
                ('Database Design', 'Design database schema', 40),
                ('UI/UX Design', 'Create wireframes and mockups', 50),
                ('API Design', 'Design API endpoints and contracts', 30)
            ],
            'Development': [
                ('Backend Development', 'Develop backend services', 120),
                ('Frontend Development', 'Develop user interface', 100),
                ('Database Implementation', 'Implement database', 60),
                ('API Implementation', 'Implement APIs', 80),
                ('Integration', 'Integrate components', 60),
                ('Code Review', 'Review and refactor code', 40)
            ],
            'Testing': [
                ('Unit Testing', 'Write and run unit tests', 50),
                ('Integration Testing', 'Test component integration', 40),
                ('User Acceptance Testing', 'Conduct UAT', 30),
                ('Performance Testing', 'Test system performance', 30)
            ],
            'Deployment': [
                ('Environment Setup', 'Setup production environment', 30),
                ('Deployment Configuration', 'Configure deployment pipeline', 25),
                ('Production Deployment', 'Deploy to production', 20),
                ('Post-Deployment Monitoring', 'Monitor system health', 25)
            ]
        }
        
        tasks = []
        for phase, phase_tasks in task_templates.items():
            for task_name, description, hours in phase_tasks:
                task = Task(
                    task_name=task_name,
                    description=description,
                    required_skills=self.project.required_skills[:2],
                    estimated_hours=hours,
                    phase=phase
                )
                tasks.append(task)
        
        self.tasks = tasks
        return tasks
    
    def allocate_tasks(self) -> List[ResourceAllocation]:
        """Allocate tasks to team members with bandwidth tracking, load balancing, and parallel execution"""
        allocations = []
        
        # Track bandwidth usage per team member per week
        # Format: {member_name: {week: bandwidth_used}}
        bandwidth_tracker = {member.name: {} for member in self.team_members}
        
        # Track earliest available week per member
        member_earliest_week = {member.name: 0 for member in self.team_members}
        
        # Group tasks by phase for proper sequencing
        phase_order = ['Planning', 'Design', 'Development', 'Testing', 'Deployment']
        tasks_by_phase = {phase: [] for phase in phase_order}
        
        for task in self.tasks:
            if task.phase in tasks_by_phase:
                tasks_by_phase[task.phase].append(task)
        
        # Track when each phase ends (for phase dependencies)
        phase_end_weeks = {}
        
        # Process tasks phase by phase (with parallel execution within each phase)
        for phase_idx, phase in enumerate(phase_order):
            phase_tasks = tasks_by_phase[phase]
            if not phase_tasks:
                continue
            
            # Determine when this phase can start
            if phase_idx == 0:
                phase_start_week = 0  # First phase starts immediately
            else:
                # Wait for previous phase to complete
                prev_phase = phase_order[phase_idx - 1]
                phase_start_week = phase_end_weeks.get(prev_phase, 0)
            
            print(f"\n    Phase: {phase} (starting week {phase_start_week})")
            
            # Reset member earliest weeks to phase start for parallel execution within phase
            for member in self.team_members:
                if member_earliest_week[member.name] < phase_start_week:
                    member_earliest_week[member.name] = phase_start_week
            
            phase_max_end_week = phase_start_week
            
            for task in phase_tasks:
                # Rank all team members by skill match AND current workload
                member_candidates = []
                for member in self.team_members:
                    matched = len(set(task.required_skills) & set(member.skills))
                    match_score = matched / len(task.required_skills) if task.required_skills else 0.3
                    
                    # Calculate current workload (prefer less busy members)
                    total_workload = sum(bandwidth_tracker[member.name].values())
                    workload_score = 1.0 / (1.0 + total_workload / 100.0)
                    
                    # Combined score: 60% skill + 40% workload balance
                    combined_score = (0.6 * match_score) + (0.4 * workload_score)
                    
                    member_candidates.append((combined_score, match_score, workload_score, member))
                
                # Sort by combined score (best first)
                member_candidates.sort(reverse=True, key=lambda x: x[0])
                
                # Try to assign to best available member
                assigned = False
                for combined_score, match_score, workload_score, member in member_candidates:
                    # Calculate task requirements
                    hours_per_week = 20  # Standard hours per week per task
                    duration_weeks = max(1, int(task.estimated_hours / hours_per_week))
                    bandwidth_needed = 50  # 50% bandwidth per task
                    
                    # Try to start from phase start or member's earliest available week
                    start_week = max(phase_start_week, member_earliest_week[member.name])
                    
                    # Check if member has bandwidth available during the required weeks
                    can_assign = True
                    for week in range(start_week, start_week + duration_weeks):
                        current_usage = bandwidth_tracker[member.name].get(week, 0)
                        if current_usage + bandwidth_needed > member.total_bandwidth_percent:
                            can_assign = False
                            break
                    
                    if can_assign:
                        # Assign task to this member
                        allocation = ResourceAllocation(
                            project=self.project,
                            task=task,
                            team_member=member,
                            start_week=start_week,
                            end_week=start_week + duration_weeks,
                            allocated_bandwidth=bandwidth_needed,
                            estimated_cost=task.estimated_hours * member.hourly_rate
                        )
                        allocations.append(allocation)
                        
                        # Update bandwidth tracker
                        for week in range(start_week, start_week + duration_weeks):
                            if week not in bandwidth_tracker[member.name]:
                                bandwidth_tracker[member.name][week] = 0
                            bandwidth_tracker[member.name][week] += bandwidth_needed
                        
                        # Update member's earliest available week
                        member_earliest_week[member.name] = start_week + duration_weeks
                        
                        # Track phase end
                        phase_max_end_week = max(phase_max_end_week, start_week + duration_weeks)
                        
                        assigned = True
                        print(f"      ✓ {task.task_name} → {member.name} (Weeks {start_week}-{start_week + duration_weeks}, Match: {match_score:.0%})")
                        break
                
                if not assigned:
                    # Fallback: assign to best candidate even if overallocated
                    if member_candidates:
                        combined_score, match_score, workload_score, member = member_candidates[0]
                        start_week = max(phase_start_week, member_earliest_week[member.name])
                        hours_per_week = 20
                        duration_weeks = max(1, int(task.estimated_hours / hours_per_week))
                        bandwidth_needed = 50
                        
                        allocation = ResourceAllocation(
                            project=self.project,
                            task=task,
                            team_member=member,
                            start_week=start_week,
                            end_week=start_week + duration_weeks,
                            allocated_bandwidth=bandwidth_needed,
                            estimated_cost=task.estimated_hours * member.hourly_rate
                        )
                        allocations.append(allocation)
                        
                        # Update bandwidth tracker (even if overallocated)
                        for week in range(start_week, start_week + duration_weeks):
                            if week not in bandwidth_tracker[member.name]:
                                bandwidth_tracker[member.name][week] = 0
                            bandwidth_tracker[member.name][week] += bandwidth_needed
                        
                        member_earliest_week[member.name] = start_week + duration_weeks
                        phase_max_end_week = max(phase_max_end_week, start_week + duration_weeks)
                        
                        print(f"      ⚠️  {task.task_name} → {member.name} (Overallocated, Weeks {start_week}-{start_week + duration_weeks})")
            
            # Record when this phase ended
            phase_end_weeks[phase] = phase_max_end_week
        
        self.allocations = allocations
        return allocations
    
    def assess_risks(self) -> List[str]:
        """Use LLM to assess project risks"""
        print(f"  🎯 Assessing risks using AI...")
        
        prompt = f"""
You are a project risk assessment expert. Analyze the following project and identify 3-5 key risks:

Project: {self.project.name}
Description: {self.project.description}
Budget: ${self.project.budget:,.0f}
Duration: {self.project.estimated_duration_weeks} weeks
Required Skills: {', '.join(self.project.required_skills)}

Provide 3-5 specific, actionable risks in bullet point format. Each risk should be one sentence.
Focus on: technical challenges, resource constraints, timeline risks, and integration issues.
"""
        
        try:
            response = self.llm.invoke(prompt)
            risks_text = response.content
            
            # Parse risks from response
            risks = [
                line.strip().lstrip('•').lstrip('-').lstrip('*').strip()
                for line in risks_text.split('\n')
                if line.strip() and len(line.strip()) > 20
            ]
            
            return risks[:5] if risks else [
                "Tight timeline may impact quality",
                "Skill gaps in required technologies",
                "Integration complexity with existing systems"
            ]
        except Exception as e:
            print(f"  ⚠️ LLM risk assessment failed: {e}")
            return [
                "Resource availability constraints may cause delays",
                "Technical complexity requires experienced team members",
                "Budget constraints may limit scope flexibility"
            ]
    
    def generate_charts(self) -> Dict[str, go.Figure]:
        """Generate project-specific charts"""
        print(f"  📊 Generating charts for {self.project.name}...")
        
        charts = {}
        
        # Chart 1: Project-Specific Gantt Chart (Fixed with proper bars)
        gantt_data = []
        # Use configured start date for timeline visualization
        try:
            base_date = datetime.strptime(self.start_date, '%Y-%m-%d') if hasattr(self, 'start_date') else datetime.now()
        except:
            base_date = datetime.now()
        
        # Phase order for proper grouping
        phase_order = ['Planning', 'Design', 'Development', 'Testing', 'Deployment']
        phase_colors = {
            'Planning': '#636EFA',
            'Design': '#EF553B', 
            'Development': '#00CC96',
            'Testing': '#AB63FA',
            'Deployment': '#FFA15A'
        }
        
        for alloc in self.allocations:
            start_date = base_date + timedelta(weeks=alloc.start_week)
            end_date = base_date + timedelta(weeks=alloc.end_week)
            
            # Create formatted task label
            task_label = f"{alloc.task.phase}: {alloc.task.task_name}"
            
            gantt_data.append({
                'Task': task_label,
                'Phase': alloc.task.phase,
                'Start': start_date,
                'Finish': end_date,
                'Resource': alloc.team_member.name,
                'Hours': alloc.task.estimated_hours,
                'Cost': alloc.estimated_cost
            })
        
        if gantt_data:
            gantt_df = pd.DataFrame(gantt_data)
            
            # Sort by phase order, then by start date
            gantt_df['PhaseOrder'] = gantt_df['Phase'].map({p: i for i, p in enumerate(phase_order)})
            gantt_df = gantt_df.sort_values(['PhaseOrder', 'Start'])
            
            # Use px.timeline for proper rendering
            fig1 = px.timeline(
                gantt_df,
                x_start='Start',
                x_end='Finish',
                y='Task',
                color='Phase',
                hover_data={
                    'Resource': True,
                    'Hours': ':.0f',
                    'Cost': ':$,.0f',
                    'Start': '|%Y-%m-%d',
                    'Finish': '|%Y-%m-%d',
                    'Phase': True
                },
                title=f'Project Timeline: {self.project.name}',
                color_discrete_map=phase_colors,
                category_orders={'Phase': phase_order}
            )
            
            fig1.update_layout(
                height=max(600, len(gantt_df) * 25),
                xaxis_title='Timeline',
                yaxis_title='Task',
                yaxis={
                    'categoryorder': 'array',
                    'categoryarray': gantt_df['Task'].tolist()
                },
                xaxis=dict(
                    tickformat='%b %d, %Y',
                    tickangle=-45
                ),
                showlegend=True,
                legend=dict(title='Phase'),
                hovermode='closest'
            )
            
            charts['project_gantt'] = fig1
        
        # Chart 2: Phase Breakdown (Improved)
        phase_data = {}
        for task in self.tasks:
            phase_data[task.phase] = phase_data.get(task.phase, 0) + task.estimated_hours
        
        # Use same colors as Gantt chart for consistency
        phase_colors = {
            'Planning': '#636EFA',
            'Design': '#EF553B', 
            'Development': '#00CC96',
            'Testing': '#AB63FA',
            'Deployment': '#FFA15A'
        }
        
        colors_list = [phase_colors.get(phase, '#999999') for phase in phase_data.keys()]
        
        # Calculate percentages
        total_hours = sum(phase_data.values())
        percentages = {phase: (hours / total_hours * 100) for phase, hours in phase_data.items()}
        
        fig2 = go.Figure(data=[go.Pie(
            labels=list(phase_data.keys()),
            values=list(phase_data.values()),
            hole=0.4,
            marker=dict(colors=colors_list, line=dict(color='white', width=2)),
            textinfo='label+percent',
            textfont=dict(size=12),
            hovertemplate=(
                "<b>%{label}</b><br>" +
                "Hours: %{value:.0f}<br>" +
                "Percentage: %{percent}<br>" +
                "<extra></extra>"
            )
        )])
        
        fig2.update_layout(
            title=f'<b>Task Distribution by Phase: {self.project.name}</b>',
            height=450,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=11)
            ),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(size=11)
        )
        
        charts['phase_breakdown'] = fig2
        
        return charts
    
    def execute(self):
        """Execute deep dive analysis"""
        tasks = self.create_detailed_tasks()
        allocations = self.allocate_tasks()
        risks = self.assess_risks()
        charts = self.generate_charts()
        
        total_cost = sum(a.estimated_cost for a in allocations)
        max_week = max([a.end_week for a in allocations]) if allocations else 0
        
        output = AgentOutput(
            agent_name="Deep Dive Agent",
            timestamp=datetime.now().isoformat(),
            data={
                'project_name': self.project.name,
                'total_tasks': len(tasks),
                'total_cost': total_cost,
                'timeline_weeks': max_week,
                'risks_identified': len(risks),
                'risks': risks
            },
            recommendations=risks
        )
        
        return output, allocations, charts

# ============================================================================
# PART 4: TRAINING RECOMMENDATION AGENT (Sub-Agent 3)
# ============================================================================

class TrainingRecommendationAgent:
    """
    Training Recommendation Agent - Identifies skill gaps and recommends courses
    """
    
    def __init__(self, team_members: List[TeamMember], projects: List[Project], llm):
        self.team_members = team_members
        self.projects = projects
        self.llm = llm
    
    def identify_skill_gaps(self) -> Dict[str, List[str]]:
        """Identify missing skills for each team member"""
        print("\n🎓 Training Agent: Identifying skill gaps...")
        
        # Get all required skills from projects
        all_required_skills = set()
        for project in self.projects:
            all_required_skills.update(project.required_skills)
        
        skill_gaps = {}
        for member in self.team_members:
            member_skills = set(member.skills)
            missing_skills = all_required_skills - member_skills
            if missing_skills:
                skill_gaps[member.name] = list(missing_skills)
        
        return skill_gaps
    
    def generate_course_recommendations(self, member: TeamMember, skill: str) -> List[Dict]:
        """Use LLM to generate specific course recommendations"""
        
        prompt = f"""
You are a professional training advisor. Generate 4 specific online course recommendations for learning: {skill}

For each course, provide:
- Platform (Coursera, Udemy, Pluralsight, LinkedIn Learning, edX, freeCodeCamp, or YouTube)
- Course title (realistic, specific course name)
- Instructor or provider
- Duration (in hours or weeks)
- Cost (Free or Paid)

Format as a numbered list with these exact details.
Make recommendations realistic and from popular platforms.
"""
        
        try:
            response = self.llm.invoke(prompt)
            courses_text = response.content
            
            # Parse courses (simplified)
            courses = []
            lines = [l.strip() for l in courses_text.split('\n') if l.strip()]
            
            current_course = {}
            for line in lines[:20]:  # Limit parsing
                if line[0].isdigit() and '.' in line[:3]:
                    if current_course:
                        courses.append(current_course)
                    current_course = {'title': line}
                elif current_course:
                    current_course['details'] = current_course.get('details', '') + ' ' + line
            
            if current_course:
                courses.append(current_course)
            
            return courses[:4] if courses else [
                {'title': f'[Coursera] {skill} Fundamentals - 4 weeks - Paid'},
                {'title': f'[Udemy] Master {skill} - 10 hours - Paid'},
                {'title': f'[freeCodeCamp] {skill} Tutorial - 3 hours - Free'},
                {'title': f'[LinkedIn Learning] {skill} Essentials - 2 hours - Paid'}
            ]
            
        except Exception as e:
            print(f"  ⚠️ LLM course generation failed: {e}")
            return [
                {'title': f'[Coursera] {skill} Fundamentals - 4 weeks'},
                {'title': f'[Udemy] Complete {skill} Course - 12 hours'},
                {'title': f'[Pluralsight] {skill} Path - 6 hours'},
                {'title': f'[freeCodeCamp] {skill} Tutorial - Free'}
            ]
    
    def generate_charts(self, skill_gaps: Dict[str, List[str]], recommendations: List[Dict]) -> Dict[str, go.Figure]:
        """Generate training-related charts"""
        print("  📊 Generating training charts...")
        
        charts = {}
        
        # Chart 1: Skills Gap Analysis
        all_missing_skills = []
        for skills in skill_gaps.values():
            all_missing_skills.extend(skills)
        
        from collections import Counter
        skill_counts = Counter(all_missing_skills)
        
        if skill_counts:
            fig1 = go.Figure(data=[go.Bar(
                x=list(skill_counts.keys()),
                y=list(skill_counts.values()),
                marker_color='coral'
            )])
            fig1.update_layout(
                title='Top Missing Skills Across Team',
                xaxis_title='Skill',
                yaxis_title='Number of Team Members',
                height=400
            )
            charts['skills_gap'] = fig1
        
        # Chart 2: Training Timeline
        training_data = []
        for rec in recommendations:
            training_data.append({
                'Member': rec['member_name'],
                'Skills': len(rec['skills_to_learn']),
                'Weeks': len(rec['skills_to_learn']) * 4
            })
        
        if training_data:
            training_df = pd.DataFrame(training_data)
            fig2 = go.Figure(data=[go.Bar(
                x=training_df['Member'],
                y=training_df['Weeks'],
                marker_color='lightblue',
                text=training_df['Skills'],
                texttemplate='%{text} skills',
                textposition='outside'
            )])
            fig2.update_layout(
                title='Estimated Training Duration per Team Member',
                xaxis_title='Team Member',
                yaxis_title='Weeks',
                height=400
            )
            charts['training_timeline'] = fig2
        
        return charts
    
    def execute(self):
        """Execute training recommendations"""
        skill_gaps = self.identify_skill_gaps()
        
        recommendations = []
        for member_name, missing_skills in skill_gaps.items():
            member = next(m for m in self.team_members if m.name == member_name)
            
            print(f"\n  📚 Generating recommendations for {member_name}...")
            
            skill_recommendations = []
            for skill in missing_skills[:3]:  # Limit to top 3 skills
                courses = self.generate_course_recommendations(member, skill)
                skill_recommendations.append({
                    'skill': skill,
                    'courses': courses,
                    'estimated_weeks': 4
                })
            
            recommendations.append({
                'member_name': member_name,
                'member_profile': member.profile,
                'skills_to_learn': missing_skills,
                'recommendations': skill_recommendations,
                'priority': 'High' if len(missing_skills) > 3 else 'Medium'
            })
        
        charts = self.generate_charts(skill_gaps, recommendations)
        
        total_training_weeks = sum(len(r['skills_to_learn']) * 4 for r in recommendations)
        
        output = AgentOutput(
            agent_name="Training Recommendation Agent",
            timestamp=datetime.now().isoformat(),
            data={
                'team_members_needing_training': len(recommendations),
                'total_skills_to_learn': sum(len(r['skills_to_learn']) for r in recommendations),
                'total_training_weeks': total_training_weeks
            },
            recommendations=[
                f"{len(recommendations)} team members need training",
                f"Total training duration: {total_training_weeks} weeks",
                "Prioritize high-priority skills first"
            ]
        )
        
        return output, recommendations, charts

# ============================================================================
# PART 5: MASTER MANAGER AGENT
# ============================================================================

class MasterManagerAgent:
    """
    Master Manager Agent - Orchestrates all sub-agents
    """
    
    def __init__(self, team_members: List[TeamMember], projects: List[Project], 
                 config: Dict, llm):
        self.team_members = team_members
        self.projects = projects
        self.config = config
        self.llm = llm
        
        # Extract config parameters with defaults
        self.start_date = config.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        self.max_weeks = config.get('max_weeks', 52)
        
        self.portfolio_results = None
        self.deep_dive_results = {}
        self.training_results = None
    
    def execute_portfolio_management(self):
        """Step 1: Execute Portfolio Manager Agent"""
        print("\n" + "="*70)
        print("STEP 1: EXECUTING PORTFOLIO MANAGER AGENT")
        print("="*70)
        
        # Pass start_date to portfolio agent via config
        portfolio_agent = PortfolioManagerAgent(self.team_members, self.projects, 
                                                 start_date=self.start_date, 
                                                 max_weeks=self.max_weeks)
        output, allocations, charts = portfolio_agent.execute()
        
        self.portfolio_results = {
            'output': output,
            'allocations': allocations,
            'charts': charts
        }
        
        return self.portfolio_results
    
    def execute_deep_dive_analysis(self):
        """Step 2: Execute Deep Dive Agent for selected projects"""
        print("\n" + "="*70)
        print("STEP 2: EXECUTING DEEP DIVE AGENT")
        print("="*70)
        
        deep_dive_names = self.config.get('deep_dive_projects', [])
        
        if not deep_dive_names:
            deep_dive_projects = [p for p in self.projects if p.priority == 1][:2]
        else:
            deep_dive_projects = [p for p in self.projects if p.name in deep_dive_names]
        
        print(f"Deep diving into {len(deep_dive_projects)} projects:")
        for p in deep_dive_projects:
            print(f"  - {p.name}")
        
        for project in deep_dive_projects:
            deep_dive_agent = DeepDiveAgent(project, self.team_members, self.llm, start_date=self.start_date)
            output, allocations, charts = deep_dive_agent.execute()
            
            self.deep_dive_results[project.name] = {
                'output': output,
                'allocations': allocations,
                'charts': charts
            }
        
        return self.deep_dive_results
    
    def execute_training_recommendations(self):
        """Step 3: Execute Training Recommendation Agent"""
        print("\n" + "="*70)
        print("STEP 3: EXECUTING TRAINING RECOMMENDATION AGENT")
        print("="*70)
        
        training_agent = TrainingRecommendationAgent(
            self.team_members,
            self.projects,
            self.llm
        )
        output, recommendations, charts = training_agent.execute()
        
        self.training_results = {
            'output': output,
            'recommendations': recommendations,
            'charts': charts
        }
        
        return self.training_results
    
    def generate_executive_summary(self):
        """Generate executive summary of all results"""
        print("\n" + "="*70)
        print("EXECUTIVE SUMMARY")
        print("="*70)
        
        portfolio_data = self.portfolio_results['output'].data
        print(f"\nPORTFOLIO OVERVIEW:")
        print(f"  Projects: {portfolio_data['projects_count']}")
        print(f"  Team Size: {portfolio_data['team_size']}")
        print(f"  Total Budget: ${sum(p.budget for p in self.projects):,.0f}")
        print(f"  Estimated Cost: ${portfolio_data['total_cost']:,.0f}")
        print(f"  Timeline: {portfolio_data['timeline_weeks']} weeks")
        print(f"  Total Allocations: {portfolio_data['total_allocations']}")
        
        if self.deep_dive_results:
            print(f"\nDEEP DIVE ANALYSIS:")
            for project_name, results in self.deep_dive_results.items():
                data = results['output'].data
                print(f"  {project_name}:")
                print(f"    - Tasks: {data['total_tasks']}")
                print(f"    - Cost: ${data['total_cost']:,.0f}")
                print(f"    - Timeline: {data['timeline_weeks']} weeks")
                print(f"    - Risks: {data['risks_identified']}")
        
        if self.training_results:
            training_data = self.training_results['output'].data
            print(f"\nTRAINING NEEDS:")
            print(f"  Team Members Needing Training: {training_data['team_members_needing_training']}")
            print(f"  Skills to Develop: {training_data['total_skills_to_learn']}")
            print(f"  Training Duration: {training_data['total_training_weeks']} weeks")
        
        print("="*70)
    
    def execute_complete_workflow(self):
        """Execute the complete master agent workflow"""
        print("\n" + "="*70)
        print("MASTER MANAGER AGENT - STARTING COMPLETE WORKFLOW")
        print("="*70)
        
        self.execute_portfolio_management()
        self.execute_deep_dive_analysis()
        self.execute_training_recommendations()
        self.generate_executive_summary()
        
        print("\n" + "="*70)
        print("MASTER MANAGER AGENT - WORKFLOW COMPLETE")
        print("="*70)
        
        return {
            'portfolio': self.portfolio_results,
            'deep_dive': self.deep_dive_results,
            'training': self.training_results,
            'status': 'Success'
        }

print("✅ Multi-Agent System Module Loaded Successfully")