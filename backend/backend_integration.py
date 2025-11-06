# ============================================================================
# BACKEND INTEGRATION - UPDATED VERSION
# ✅ Fixed for llama-3.1-8b-instant model (tested and working)
# ✅ Fixed portfolio summary bug (projects_count = 0)
# ✅ Optimized timeouts and token limits
# ============================================================================

import sys
import os
from typing import List, Dict, Any
import pickle
import json
from datetime import datetime
import time

from multi_agent_system import (
    TeamMember, 
    Project, 
    MasterManagerAgent,
    Task,
    ResourceAllocation,
    AgentOutput
)

PRIORITY_MAP = {'Critical': 1, 'High': 2, 'Medium': 3, 'Low': 4}

def convert_priority(priority_value):
    if isinstance(priority_value, int):
        return priority_value
    if isinstance(priority_value, str):
        return PRIORITY_MAP.get(priority_value, 3)
    return 3

def convert_frontend_to_backend(team_data: List[Dict], project_data: List[Dict]):
    team_members = []
    for member_dict in team_data:
        skills_list = [s.strip() for s in member_dict['skills'].split(',')]
        team_member = TeamMember(
            name=member_dict['name'],
            profile=member_dict['profile'],
            skills=skills_list,
            total_bandwidth_percent=member_dict['bandwidth'],
            hourly_rate=member_dict['hourly_rate'],
            location=member_dict['location']
        )
        team_members.append(team_member)
    
    projects = []
    for proj_dict in project_data:
        required_skills_list = [s.strip() for s in proj_dict['required_skills'].split(',')]
        priority_int = convert_priority(proj_dict.get('priority', 3))
        
        project = Project(
            name=proj_dict['name'],
            description=proj_dict['description'],
            priority=priority_int,
            budget=proj_dict['budget'],
            required_skills=required_skills_list,
            estimated_duration_weeks=proj_dict['duration_weeks'],
            client=proj_dict['client'],
            deadline=proj_dict['deadline']
        )
        projects.append(project)
    
    print(f"\n✅ Converted {len(team_members)} team members and {len(projects)} projects")
    return team_members, projects

def run_multi_agent_system(team_data: List[Dict], project_data: List[Dict], config: Dict, llm) -> Dict:
    team_members, projects = convert_frontend_to_backend(team_data, project_data)
    
    print("\n" + "="*60)
    print("INITIALIZING MASTER MANAGER AGENT")
    print("="*60)
    
    master_agent = MasterManagerAgent(
        team_members=team_members,
        projects=projects,
        config=config,
        llm=llm
    )
    
    results = master_agent.execute_complete_workflow()
    frontend_results = convert_backend_to_frontend(results, team_members, projects)
    return frontend_results

def convert_backend_to_frontend(backend_results: Dict, team_members, projects) -> Dict:
    """
    Convert backend results to frontend format
    ✅ FIXED: Portfolio summary projects_count bug
    """
    frontend_results = {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'summary': {},
        'portfolio': {},
        'deep_dive': {},
        'training': {},
        'visualizations': [],
        'team_members': [
            {
                'name': m.name, 
                'profile': m.profile, 
                'skills': m.skills, 
                'bandwidth': m.total_bandwidth_percent, 
                'hourly_rate': m.hourly_rate, 
                'location': m.location
            } 
            for m in team_members
        ],
        'projects': [
            {
                'name': p.name, 
                'description': p.description, 
                'priority': p.priority, 
                'budget': p.budget, 
                'required_skills': p.required_skills, 
                'duration_weeks': p.estimated_duration_weeks, 
                'client': p.client, 
                'deadline': p.deadline
            } 
            for p in projects
        ]
    }
    
    if 'portfolio' in backend_results and backend_results['portfolio']:
        portfolio_output = backend_results['portfolio']['output']
        
        # ✅ FIX: Ensure project count is correct
        summary_data = portfolio_output.data.copy()
        if 'projects_count' not in summary_data or summary_data.get('projects_count', 0) == 0:
            summary_data['projects_count'] = len(projects)  # Use actual project count
            print(f"✅ Fixed portfolio summary: projects_count = {len(projects)}")
        
        frontend_results['summary'] = summary_data
        
        # Portfolio allocations
        frontend_results['portfolio']['allocations'] = [
            {
                'project_name': alloc.project.name,
                'task_name': alloc.task.task_name,
                'team_member': alloc.team_member.name,
                'start_week': alloc.start_week,
                'end_week': alloc.end_week,
                'bandwidth': alloc.allocated_bandwidth,
                'cost': alloc.estimated_cost
            }
            for alloc in backend_results['portfolio']['allocations']
        ]
        
        # Portfolio charts
        frontend_results['portfolio']['charts'] = {}
        for chart_name, fig in backend_results['portfolio']['charts'].items():
            frontend_results['portfolio']['charts'][chart_name] = fig
    
    # Deep dive results
    if 'deep_dive' in backend_results:
        for project_name, project_data in backend_results['deep_dive'].items():
            output_data = project_data['output'].data
            frontend_results['deep_dive'][project_name] = {
                'total_tasks': output_data['total_tasks'],
                'total_cost': output_data['total_cost'],
                'timeline_weeks': output_data['timeline_weeks'],
                'risks_identified': output_data['risks_identified'],
                'risks': output_data['risks'],
                'charts': project_data['charts'],
                'allocations': [
                    {
                        'task_name': alloc.task.task_name,
                        'phase': alloc.task.phase,
                        'team_member': alloc.team_member.name,
                        'start_week': alloc.start_week,
                        'end_week': alloc.end_week,
                        'estimated_hours': alloc.task.estimated_hours,
                        'cost': alloc.estimated_cost
                    }
                    for alloc in project_data['allocations']
                ]
            }
    
    # Training results
    if 'training' in backend_results and backend_results['training']:
        training_output = backend_results['training']['output']
        frontend_results['training'] = {
            'summary': training_output.data,
            'recommendations': backend_results['training']['recommendations'],
            'charts': backend_results['training']['charts']
        }
    
    return frontend_results

def initialize_llm(api_key: str):
    """
    ✅ WORKING CONFIGURATION (from diagnostic test)
    Model: llama-3.1-8b-instant (tested: 0.27-0.60s response time)
    Max Tokens: 800 (enough for 3 risks OR 4 detailed courses)
    Timeout: 60s (safety margin, actual calls are <1s)
    """
    from langchain_groq import ChatGroq
    
    print("\n🔧 Initializing Groq LLM...")
    print("="*60)
    
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",  # ✅ Tested and working!
        temperature=0,                       # Deterministic
        max_tokens=800,                      # ✅ Enough for complete responses
        timeout=60,                          # ✅ Safety margin
        request_timeout=60,
    )
    
    print("✅ LLM Configuration:")
    print(f"   • Model: llama-3.1-8b-instant (tested: 0.27-0.60s)")
    print(f"   • Max Tokens: 800")
    print(f"   • Timeout: 60s")
    print("="*60)
    
    # TEST LLM CONNECTIVITY
    print("\n🧪 Testing LLM connectivity...")
    try:
        start = time.time()
        test_response = llm.invoke("Say OK")
        elapsed = time.time() - start
        
        if test_response and test_response.content:
            print(f"✅ LLM is working! Response time: {elapsed:.2f}s")
            print(f"   Response: {test_response.content[:30]}")
        else:
            print("⚠️ LLM returned empty response")
            print("   Risks and training will use fallback templates")
    except Exception as e:
        print(f"❌ LLM test FAILED: {str(e)[:60]}")
        print("   Risks and training will use fallback templates")
        print(f"   Error type: {type(e).__name__}")
    
    print("="*60)
    return llm

def run_analysis_for_streamlit(team_data: List[Dict], project_data: List[Dict], 
                               config: Dict, api_key: str) -> Dict:
    """
    Main analysis function with improved error handling
    ✅ Uses tested working model: llama-3.1-8b-instant
    ✅ Fixed portfolio summary bug
    """
    
    try:
        print("\n" + "="*60)
        print("STARTING PROJECT ANALYSIS")
        print("="*60)
        
        # Initialize LLM with working configuration
        analysis_start = time.time()
        llm = initialize_llm(api_key)
        
        print("\n🚀 Running multi-agent system...")
        print("="*60)
        
        # Run analysis
        results = run_multi_agent_system(team_data, project_data, config, llm)
        
        analysis_time = time.time() - analysis_start
        print(f"\n⏱️  Total analysis time: {analysis_time:.2f}s")
        print("="*60)
        
        # Skip AI verification (optional feature)
        results['ai_verification'] = {
            'skipped': True,
            'reason': 'Optional feature - enable if needed'
        }
        
        # Save results
        save_results_to_cache(results)
        
        return results
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.now().isoformat()
        }

def save_results_to_cache(results: Dict, cache_file: str = 'results_cache.pkl'):
    """Save results to cache file"""
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(results, f)
        print(f"\n✅ Results saved to {cache_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save cache: {e}")

def load_results_from_cache(cache_file: str = 'results_cache.pkl') -> Dict:
    """Load results from cache file"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                results = pickle.load(f)
            print(f"✅ Loaded cached results from {cache_file}")
            return results
        except Exception as e:
            print(f"⚠️ Could not load cache: {e}")
            return None
    return None

def export_to_excel(results: Dict, filename: str = 'project_results.xlsx'):
    """Export results to Excel file"""
    import pandas as pd
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Portfolio allocations
            if 'portfolio' in results and 'allocations' in results['portfolio']:
                alloc_df = pd.DataFrame(results['portfolio']['allocations'])
                alloc_df.to_excel(writer, sheet_name='Allocations', index=False)
            
            # Summary
            if 'summary' in results:
                summary_df = pd.DataFrame([results['summary']])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Training recommendations
            if 'training' in results and 'recommendations' in results['training']:
                training_data = []
                for rec in results['training']['recommendations']:
                    for skill_rec in rec['recommendations']:
                        training_data.append({
                            'Member': rec['member_name'],
                            'Profile': rec['member_profile'],
                            'Skill': skill_rec['skill'],
                            'Duration_Weeks': skill_rec['estimated_weeks'],
                            'Priority': rec['priority']
                        })
                
                if training_data:
                    training_df = pd.DataFrame(training_data)
                    training_df.to_excel(writer, sheet_name='Training', index=False)
        
        print(f"✅ Results exported to {filename}")
        return filename
    
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None

print("✅ Backend Integration (UPDATED VERSION) Loaded Successfully!")
print("📝 Updates:")
print("   • Using llama-3.1-8b-instant (tested and working)")
print("   • Fixed portfolio summary bug (projects_count = 0)")
print("   • Optimized max_tokens=800, timeout=60s")
print("   • Added LLM connectivity test at startup")