# ============================================================================
# AI PROJECT MANAGER - ULTRA-SIMPLIFIED VERSION
# No complex HTML, all issues fixed
# ============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict
import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend')
if os.path.exists(backend_path):
    sys.path.insert(0, backend_path)
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

st.set_page_config(
    page_title="AI Project Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2C3E50;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7F8C8D;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'team_members' not in st.session_state:
    st.session_state.team_members = []
if 'projects' not in st.session_state:
    st.session_state.projects = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🤖 AI PM")
    st.markdown("---")
    
    st.markdown("### Navigation")
    pages = {
        "🏠 Home": "Home",
        "👥 Team Input": "Team Input",
        "📁 Project Input": "Project Input",
        "🚀 Run Analysis": "Run Analysis",
        "📊 Dashboard": "Dashboard"
    }
    
    for label, page in pages.items():
        if st.button(label, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    st.metric("Team Members", len(st.session_state.team_members))
    st.metric("Projects", len(st.session_state.projects))
    
    if st.session_state.analysis_results:
        st.metric("Analysis", "✅ Complete")
    else:
        st.metric("Analysis", "⏳ Pending")

# ============================================================================
# PAGE 1: HOME - SIMPLIFIED (NO COMPLEX HTML)
# ============================================================================

def page_home():
    st.markdown('<h1 class="main-header">🤖 AI Project Manager</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent resource allocation powered by multi-agent AI</p>', unsafe_allow_html=True)
    
    # Simple info boxes using Streamlit native components
    st.info("📊 **AI-Powered Project Management**\n\nAutomatically allocates resources across multiple projects using a sophisticated multi-agent architecture.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**✨ Key Benefits**")
        st.write("• Smart Allocation: 30% skill + 50% workload + 20% penalty")
        st.write("• AI Risk Assessment")
        st.write("• Training Recommendations")
        st.write("• Interactive Visualizations")
    
    with col2:
        st.warning("**🎯 Features**")
        st.write("• Automated resource allocation")
        st.write("• Multi-project balancing")
        st.write("• Skill gap analysis")
        st.write("• Gantt charts & heatmaps")
    
    st.markdown("---")
    st.markdown("## 🏗️ System Architecture")
    
    # SIMPLIFIED ARCHITECTURE - Using Streamlit native components only
    st.write("**📥 Input Layer:** Team Data → Project Data → Configuration")
    st.write("**⬇️**")
    st.write("**🤖 Master Manager:** Orchestrates workflow and coordinates agents")
    st.write("**⬇️**")
    st.write("**🔄 Specialized Agents:**")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("**Portfolio Manager**\n\nResource allocation")
    with col2:
        st.info("**Deep Dive**\n\nTask breakdown")
    with col3:
        st.info("**Training**\n\nSkill analysis")
    with col4:
        st.info("**Visualization**\n\nCharts & reports")
    
    st.write("**⬇️**")
    st.write("**📤 Output Layer:** Optimized Allocations + Risk Insights + Training Plans")
    
    st.markdown("---")
    st.markdown("## 💻 Technology Stack")
    
    # SIMPLE TEXT - No HTML formatting issues
    st.write("**AI/ML:** LangChain, Groq LLM (Llama models)")
    st.write("**Data Processing:** Pydantic, Pandas, NumPy")
    st.write("**Visualization:** Plotly, Streamlit")
    st.write("**Architecture:** Multi-Agent System")
    
    st.markdown("---")
    st.markdown("## 🔮 Future Enhancements")
    
    # SIMPLE TEXT - No HTML list formatting
    st.write("**Jira Integration** - Direct task synchronization")
    st.write("**Plainsware Integration** - Enterprise planning tools")
    st.write("**Employee Database** - Persistent team profile storage")
    
    st.markdown("---")
    st.success("🚀 **Ready to start?** Go to Team Input to add your team members!")

# ============================================================================
# PAGE 2: TEAM INPUT
# ============================================================================

def page_team_input():
    st.markdown('<h1 class="main-header">👥 Team Members</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Add your team members with their skills and availability</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("📋 Load Sample Data", use_container_width=True):
            st.session_state.team_members = [
                {'name': 'Alice Johnson', 'profile': 'Senior Developer', 'skills': 'Python, React, AWS, Docker', 'bandwidth': 80, 'hourly_rate': 75, 'location': 'New York, US'},
                {'name': 'Bob Smith', 'profile': 'Junior Developer', 'skills': 'Python, REST APIs, Testing', 'bandwidth': 90, 'hourly_rate': 45, 'location': 'Remote'},
                {'name': 'Charlie Davis', 'profile': 'DevOps Engineer', 'skills': 'AWS, Docker, Jenkins, Kubernetes', 'bandwidth': 75, 'hourly_rate': 70, 'location': 'San Francisco, US'},
                {'name': 'Diana Lee', 'profile': 'Full Stack Developer', 'skills': 'React Native, Node.js, MongoDB', 'bandwidth': 85, 'hourly_rate': 65, 'location': 'Austin, US'},
                {'name': 'Eve Martinez', 'profile': 'Integration Specialist', 'skills': 'SnapLogic, REST APIs, Java, Leadership', 'bandwidth': 70, 'hourly_rate': 80, 'location': 'Chicago, US'}
            ]
            st.success("✅ Sample data loaded!")
            st.rerun()
    
    with st.expander("➕ Add New Team Member", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", placeholder="John Doe")
            profile = st.text_input("Profile *", placeholder="Junior Developer")
            skills = st.text_input("Skills (comma-separated) *", placeholder="Python, AWS, React")
        
        with col2:
            bandwidth = st.slider("Bandwidth Availability (%)", 0, 100, 80)
            hourly_rate = st.number_input("Hourly Rate ($)", min_value=0, value=50, step=5)
            location = st.text_input("Location", placeholder="New York, US")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Add Team Member", use_container_width=True):
                if name and profile and skills:
                    member = {'name': name, 'profile': profile, 'skills': skills, 'bandwidth': bandwidth, 'hourly_rate': hourly_rate, 'location': location}
                    st.session_state.team_members.append(member)
                    st.success(f"✅ Added {name} to the team!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.team_members = []
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"### 📋 Current Team ({len(st.session_state.team_members)} members)")
    
    if st.session_state.team_members:
        df = pd.DataFrame(st.session_state.team_members)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Members", len(st.session_state.team_members))
        with col2:
            st.metric("Avg Bandwidth", f"{df['bandwidth'].mean():.0f}%")
        with col3:
            st.metric("Avg Hourly Rate", f"${df['hourly_rate'].mean():.0f}")
        with col4:
            total_skills = len(set([s.strip() for member in st.session_state.team_members for s in member['skills'].split(',')]))
            st.metric("Unique Skills", total_skills)
        
        st.markdown("### 📊 Skill Distribution")
        all_skills = [s.strip() for member in st.session_state.team_members for s in member['skills'].split(',')]
        skill_counts = pd.Series(all_skills).value_counts()
        fig = px.bar(x=skill_counts.values, y=skill_counts.index, orientation='h', title="Skills Across Team", labels={'x': 'Number of Members', 'y': 'Skill'})
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### ✏️ Manage Team")
        member_to_delete = st.selectbox("Select member to remove", options=[m['name'] for m in st.session_state.team_members], key="delete_member")
        if st.button("🗑️ Remove Selected Member"):
            st.session_state.team_members = [m for m in st.session_state.team_members if m['name'] != member_to_delete]
            st.success(f"Removed {member_to_delete}")
            st.rerun()
    else:
        st.info("👆 Add your first team member using the form above")
    
    if len(st.session_state.team_members) > 0:
        st.success("✅ Team members added! Next, go to **Project Input** to define your projects.")

# ============================================================================
# PAGE 3: PROJECT INPUT
# ============================================================================

def page_project_input():
    st.markdown('<h1 class="main-header">📁 Projects</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Define your projects with requirements and priorities</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("📋 Load Sample Data", use_container_width=True):
            st.session_state.projects = [
                {'name': 'Customer Portal Redesign', 'description': 'Complete overhaul of customer-facing web portal', 'priority': 'Critical', 'required_skills': 'React, Python, AWS, Docker', 'budget': 75000, 'duration_weeks': 16, 'client': 'Acme Corp', 'deadline': (datetime.now() + timedelta(days=120)).date().isoformat()},
                {'name': 'Mobile App Development', 'description': 'Native iOS and Android app', 'priority': 'High', 'required_skills': 'React Native, REST APIs, Mobile Development', 'budget': 50000, 'duration_weeks': 12, 'client': 'TechStart Inc', 'deadline': (datetime.now() + timedelta(days=90)).date().isoformat()},
                {'name': 'API Integration Platform', 'description': 'Build scalable API integration platform', 'priority': 'High', 'required_skills': 'SnapLogic, Resolver API, REST APIs', 'budget': 60000, 'duration_weeks': 14, 'client': 'Enterprise Solutions', 'deadline': (datetime.now() + timedelta(days=100)).date().isoformat()}
            ]
            st.success("✅ Sample project data loaded!")
            st.rerun()
    
    with st.expander("➕ Add New Project", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            proj_name = st.text_input("Project Name *", placeholder="Customer Portal Redesign")
            description = st.text_area("Description *", placeholder="Redesign the customer portal")
            priority = st.selectbox("Priority *", ["Critical", "High", "Medium", "Low"])
            required_skills = st.text_input("Required Skills (comma-separated) *", placeholder="React, Python, AWS")
        
        with col2:
            budget = st.number_input("Budget ($)", min_value=0, value=50000, step=1000)
            duration_weeks = st.number_input("Estimated Duration (weeks)", min_value=1, value=12, step=1)
            client = st.text_input("Client", placeholder="Acme Corp")
            deadline = st.date_input("Deadline", value=datetime.now() + timedelta(days=90))
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("✅ Add Project", use_container_width=True):
                if proj_name and description and required_skills:
                    project = {'name': proj_name, 'description': description, 'priority': priority, 'required_skills': required_skills, 'budget': budget, 'duration_weeks': duration_weeks, 'client': client, 'deadline': deadline.isoformat()}
                    st.session_state.projects.append(project)
                    st.success(f"✅ Added project: {proj_name}")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.projects = []
                st.rerun()
    
    st.markdown("---")
    st.markdown(f"### 📋 Current Projects ({len(st.session_state.projects)} projects)")
    
    if st.session_state.projects:
        df = pd.DataFrame(st.session_state.projects)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Projects", len(st.session_state.projects))
        with col2:
            st.metric("Total Budget", f"${df['budget'].sum():,.0f}")
        with col3:
            st.metric("Avg Duration", f"{df['duration_weeks'].mean():.1f} weeks")
        
        st.markdown("### 📊 Project Priority Distribution")
        priority_counts = df['priority'].value_counts()
        fig = px.pie(values=priority_counts.values, names=priority_counts.index, title="Projects by Priority")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### ✏️ Manage Projects")
        project_to_delete = st.selectbox("Select project to remove", options=[p['name'] for p in st.session_state.projects], key="delete_project")
        if st.button("🗑️ Remove Selected Project"):
            st.session_state.projects = [p for p in st.session_state.projects if p['name'] != project_to_delete]
            st.success(f"Removed {project_to_delete}")
            st.rerun()
    else:
        st.info("👆 Add your first project using the form above")
    
    if len(st.session_state.projects) > 0:
        st.success("✅ Projects added! Next, go to **Run Analysis** to process your data.")

# ============================================================================
# PAGE 4: RUN ANALYSIS
# ============================================================================

def page_run_analysis():
    st.markdown('<h1 class="main-header">🚀 Run AI Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Configure and execute the multi-agent analysis</p>', unsafe_allow_html=True)
    
    if len(st.session_state.team_members) == 0 or len(st.session_state.projects) == 0:
        st.warning("⚠️ Please add team members and projects before running the analysis.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Team Members"):
                st.session_state.page = "Team Input"
                st.rerun()
        with col2:
            if st.button("➕ Add Projects"):
                st.session_state.page = "Project Input"
                st.rerun()
        return
    
    st.markdown("### ⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_key = st.text_input("Groq API Key *", type="password", help="Get your API key from https://console.groq.com")
        start_date = st.date_input("Start Date", value=datetime.now())
        max_weeks = st.number_input("Max Timeline (weeks)", min_value=4, max_value=104, value=52, step=4)
    
    with col2:
        deep_dive_projects = st.multiselect(
            "Select projects for deep dive analysis",
            options=[p['name'] for p in st.session_state.projects],
            default=[p['name'] for p in st.session_state.projects][:2]
        )
    
    st.markdown("### 📊 Preview")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Team:** {len(st.session_state.team_members)} members")
        st.info(f"**Projects:** {len(st.session_state.projects)} projects")
    with col2:
        st.info(f"**Deep Dive:** {len(deep_dive_projects)} projects")
        st.info(f"**Timeline:** {max_weeks} weeks")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Run AI Analysis", use_container_width=True, type="primary"):
            if not api_key:
                st.error("Please provide your Groq API key")
                return
            
            with st.spinner("🤖 Running multi-agent analysis... This may take 1-2 minutes."):
                try:
                    from backend_integration import run_analysis_for_streamlit
                    
                    config = {
                        'deep_dive_projects': deep_dive_projects,
                        'start_date': start_date.isoformat(),
                        'max_weeks': max_weeks
                    }
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("Initializing LLM...")
                    progress_bar.progress(20)
                    
                    status_text.text("Running Portfolio Manager Agent...")
                    progress_bar.progress(40)
                    
                    results = run_analysis_for_streamlit(
                        st.session_state.team_members,
                        st.session_state.projects,
                        config,
                        api_key
                    )
                    
                    status_text.text("Running Deep Dive Analyzer...")
                    progress_bar.progress(60)
                    
                    status_text.text("Generating Training Recommendations...")
                    progress_bar.progress(80)
                    
                    status_text.text("Creating Visualizations...")
                    progress_bar.progress(100)
                    
                    if results and results.get('status') == 'success':
                        st.session_state.analysis_results = results
                        st.success("✅ Analysis complete! Navigate to Dashboard to view results.")
                        if st.button("📊 View Dashboard"):
                            st.session_state.page = "Dashboard"
                            st.rerun()
                    else:
                        error_msg = results.get('error', 'Unknown error') if results else 'Analysis failed'
                        st.error(f"❌ Analysis failed: {error_msg}")
                        if results and results.get('suggestion'):
                            st.info(results['suggestion'])
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    with st.expander("Show error details"):
                        st.code(traceback.format_exc())

# ============================================================================
# PAGE 5: DASHBOARD
# ============================================================================

def page_dashboard():
    st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analysis Results and Insights</p>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_results:
        st.warning("⚠️ No analysis results available. Please run the analysis first.")
        if st.button("🚀 Run Analysis"):
            st.session_state.page = "Run Analysis"
            st.rerun()
        return
    
    results = st.session_state.analysis_results
    
    if 'summary' in results and results['summary']:
        st.markdown("### 📋 Portfolio Summary")
        summary = results['summary']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", summary.get('projects_count', 0))
        with col2:
            st.metric("Total Cost", f"${summary.get('total_cost', 0):,.0f}")
        with col3:
            st.metric("Timeline", f"{summary.get('timeline_weeks', 0)} weeks")
        with col4:
            st.metric("Utilization", f"{summary.get('team_utilization', 0):.1f}%")
    
    if 'portfolio' in results and 'allocations' in results['portfolio']:
        st.markdown("### 📊 Resource Allocations")
        alloc_df = pd.DataFrame(results['portfolio']['allocations'])
        st.dataframe(alloc_df, use_container_width=True, hide_index=True)
        
        if 'charts' in results['portfolio']:
            for chart_name, fig in results['portfolio']['charts'].items():
                if fig:
                    st.markdown(f"#### {chart_name}")
                    st.plotly_chart(fig, use_container_width=True)
    
    if 'deep_dive' in results:
        st.markdown("### 🔍 Deep Dive Analysis")
        for project_name, project_data in results['deep_dive'].items():
                with st.expander(f"📁 {project_name}"):
                    # Project Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tasks", project_data.get('total_tasks', 0))
                    with col2:
                        st.metric("Cost", f"${project_data.get('total_cost', 0):,.0f}")
                    with col3:
                        st.metric("Timeline", f"{project_data.get('timeline_weeks', 0)} weeks")
                    
                    # Risk Assessment
                    if 'risks' in project_data and project_data['risks']:
                        st.markdown("#### 🎯 Risk Assessment")
                        for risk in project_data['risks']:
                            st.warning(risk)
                    
                    # Task Allocations
                    if 'allocations' in project_data:
                        st.markdown("#### 📋 Task Allocations")
                        alloc_df = pd.DataFrame(project_data['allocations'])
                        st.dataframe(alloc_df, use_container_width=True, hide_index=True)
                    
                    # Visualizations
                    if 'charts' in project_data:
                        st.markdown("#### 📊 Visualizations")
                        for chart_name, fig in project_data['charts'].items():
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
    
    if 'training' in results and results['training']:
        st.markdown("### 📚 Training Recommendations")
        training = results['training']
        
        if 'summary' in training:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Team Members Needing Training", 
                         training['summary'].get('team_members_needing_training', 0))
            with col2:
                st.metric("Total Skills to Learn",
                         training['summary'].get('total_skills_to_learn', 0))
            with col3:
                st.metric("Training Duration",
                         f"{training['summary'].get('total_training_weeks', 0)} weeks")
        
        if 'recommendations' in training:
            for rec in training['recommendations']:
                with st.expander(f"👤 {rec['member_name']} - {rec['member_profile']}"):
                    st.write(f"**Priority:** {rec.get('priority', 'N/A')}")
                    st.write(f"**Skills to Learn:** {', '.join(rec.get('skills_to_learn', []))}")
                    
                    if 'recommendations' in rec:
                        st.markdown("#### 📚 Recommended Courses")
                        for skill_rec in rec['recommendations']:
                            st.markdown(f"**{skill_rec['skill']}** ({skill_rec.get('estimated_weeks', 'N/A')} weeks)")
                            for course in skill_rec.get('courses', []):
                                st.info(course['title'])
        
        if 'charts' in training:
            st.markdown("#### 📊 Training Analytics")
            for chart_name, fig in training['charts'].items():
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Download Excel", use_container_width=True):
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
                from backend_integration import export_to_excel
                filename = export_to_excel(results)
                st.success(f"✅ Exported to {filename}")
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col2:
        if st.button("📋 Copy JSON", use_container_width=True):
            st.code(json.dumps(results, indent=2))
    
    with col3:
        if st.button("🔄 Run New Analysis", use_container_width=True):
            st.session_state.analysis_results = None
            st.session_state.page = "Run Analysis"
            st.rerun()

# ============================================================================
# MAIN APP
# ============================================================================

page_functions = {
    "Home": page_home,
    "Team Input": page_team_input,
    "Project Input": page_project_input,
    "Run Analysis": page_run_analysis,
    "Dashboard": page_dashboard
}

current_page = st.session_state.page
if current_page in page_functions:
    page_functions[current_page]()
else:
    page_home()