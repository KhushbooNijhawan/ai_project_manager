# ============================================================================
# AI-POWERED ALLOCATION VERIFICATION
# Uses LLM to verify and validate resource allocation decisions
# ============================================================================

from typing import List, Dict, Any
from pydantic import BaseModel
import json

class AIAllocationVerifier:
    """
    AI-powered verification system that uses LLM to:
    1. Verify allocation decisions make sense
    2. Check if scoring criteria are applied correctly
    3. Identify potential issues in allocation logic
    4. Validate consecutive task penalties
    5. Assess overall allocation quality
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.verification_results = []
    
    def verify_allocation_logic(self, allocations: List, team_members: List, projects: List) -> Dict:
        """
        Use AI to verify if allocations follow the correct logic:
        - 30% skill matching
        - 50% workload balancing
        - 20% consecutive task penalty (50% drop after 3 consecutive)
        """
        print("\n🤖 AI Verification: Analyzing allocation decisions...")
        
        # Prepare allocation summary for AI
        allocation_summary = self._prepare_allocation_summary(allocations, team_members)
        
        # Create verification prompt
        prompt = f"""
You are an expert resource allocation auditor. Analyze the following resource allocations and verify if they follow the correct logic.

ALLOCATION RULES:
1. Skill Matching (30% weight): Team members should be assigned to tasks matching their skills
2. Workload Balancing (50% weight): Work should be distributed evenly across team members
3. Consecutive Task Penalty (20% weight): After 3 consecutive task assignments to the same person, their score should drop by 50%

TEAM MEMBERS:
{json.dumps([{{'name': m['name'], 'skills': m['skills'], 'bandwidth': m['bandwidth']}} for m in team_members], indent=2)}

ALLOCATIONS:
{json.dumps(allocation_summary, indent=2)}

VERIFICATION TASKS:
1. Check if team members are assigned tasks matching their skills (30% weight being applied?)
2. Check if workload is balanced across team members (50% weight being applied?)
3. Check for consecutive task assignments - identify any member with 3+ consecutive tasks
4. Verify if the 50% penalty is being applied after 3 consecutive tasks
5. Identify any violations or suspicious patterns

Provide your analysis in JSON format:
{{
    "skill_matching_correct": true/false,
    "workload_balanced": true/false,
    "consecutive_penalty_applied": true/false,
    "violations": ["list of violations found"],
    "warnings": ["list of potential issues"],
    "overall_quality_score": 0-100,
    "recommendations": ["list of improvements"]
}}
"""
        
        try:
            # Get AI verification
            response = self.llm.invoke(prompt)
            result = self._parse_ai_response(response.content)
            
            print(f"\n✅ AI Verification Complete:")
            print(f"  - Skill Matching: {'✓' if result.get('skill_matching_correct') else '✗'}")
            print(f"  - Workload Balance: {'✓' if result.get('workload_balanced') else '✗'}")
            print(f"  - Consecutive Penalty: {'✓' if result.get('consecutive_penalty_applied') else '✗'}")
            print(f"  - Overall Quality: {result.get('overall_quality_score', 0)}/100")
            
            if result.get('violations'):
                print(f"\n❌ Violations Found: {len(result['violations'])}")
                for v in result['violations'][:3]:
                    print(f"   - {v}")
            
            if result.get('warnings'):
                print(f"\n⚠️ Warnings: {len(result['warnings'])}")
                for w in result['warnings'][:3]:
                    print(f"   - {w}")
            
            return result
            
        except Exception as e:
            print(f"⚠️ AI Verification failed: {str(e)}")
            return {
                'error': str(e),
                'overall_quality_score': 0
            }
    
    def verify_individual_allocation(self, allocation: Dict, all_allocations: List, 
                                     team_members: List) -> Dict:
        """Verify a single allocation decision using AI"""
        
        # Count consecutive assignments
        member_name = allocation['team_member']
        consecutive_count = self._count_consecutive_assignments(member_name, all_allocations)
        
        # Get member skills
        member = next((m for m in team_members if m['name'] == member_name), None)
        if not member:
            return {'error': 'Member not found'}
        
        prompt = f"""
Analyze this resource allocation decision:

ALLOCATION:
- Task: {allocation['task_name']}
- Assigned to: {member_name}
- Member Skills: {member['skills']}
- Required Skills: {allocation.get('required_skills', 'N/A')}
- Consecutive Assignments: {consecutive_count}
- Start Week: {allocation['start_week']}
- Duration: {allocation['end_week'] - allocation['start_week']} weeks

VERIFICATION:
1. Does the member have matching skills? (30% weight)
2. Is the member overloaded? (50% weight consideration)
3. Has consecutive penalty been applied if needed? ({consecutive_count} consecutive tasks)
   - Should apply 50% penalty if >= 3 consecutive

Rate this allocation (0-100) and explain if the scoring rules were followed correctly.
Format: {{"score": 0-100, "explanation": "brief explanation", "issues": []}}
"""
        
        try:
            response = self.llm.invoke(prompt)
            result = self._parse_ai_response(response.content)
            result['consecutive_count'] = consecutive_count
            result['should_have_penalty'] = consecutive_count >= 3
            return result
        except Exception as e:
            return {'error': str(e), 'consecutive_count': consecutive_count}
    
    def verify_scoring_weights(self, allocations: List, team_members: List) -> Dict:
        """
        Verify if the scoring weights (30/50/20) are being applied correctly
        """
        print("\n🔍 Verifying Scoring Weights...")
        
        # Analyze patterns in allocations
        skill_matches = []
        workload_distribution = {}
        consecutive_patterns = {}
        
        for alloc in allocations:
            member_name = alloc['team_member']
            
            # Track workload
            if member_name not in workload_distribution:
                workload_distribution[member_name] = 0
            workload_distribution[member_name] += 1
            
            # Track consecutive
            if member_name not in consecutive_patterns:
                consecutive_patterns[member_name] = []
            consecutive_patterns[member_name].append(alloc['task_name'])
        
        # Calculate workload variance (should be low if 50% weight is working)
        workload_values = list(workload_distribution.values())
        workload_variance = sum((x - sum(workload_values)/len(workload_values))**2 
                               for x in workload_values) / len(workload_values)
        
        # Check consecutive patterns
        members_with_3plus = sum(1 for tasks in consecutive_patterns.values() if len(tasks) >= 3)
        
        prompt = f"""
Analyze if the allocation weights are being applied correctly:

EXPECTED WEIGHTS:
- Skill Matching: 30%
- Workload Balancing: 50%
- Consecutive Penalty: 20% (50% drop after 3 consecutive)

ACTUAL PATTERNS:
- Workload Distribution: {workload_distribution}
- Workload Variance: {workload_variance:.2f} (lower is better)
- Members with 3+ consecutive tasks: {members_with_3plus}
- Total Allocations: {len(allocations)}

ANALYSIS:
1. Is workload well-balanced (suggesting 50% weight is working)?
2. Are there patterns suggesting skill matching (30%) is secondary to workload?
3. Is consecutive penalty being applied (members with 3+ consecutive tasks should be rare)?

Provide assessment:
{{
    "weight_application_correct": true/false,
    "confidence": 0-100,
    "issues": ["specific issues found"],
    "evidence": "evidence supporting your conclusion"
}}
"""
        
        try:
            response = self.llm.invoke(prompt)
            result = self._parse_ai_response(response.content)
            result['workload_variance'] = workload_variance
            result['members_with_3plus_consecutive'] = members_with_3plus
            
            print(f"\n✅ Weight Verification:")
            print(f"  - Correct Application: {'✓' if result.get('weight_application_correct') else '✗'}")
            print(f"  - Confidence: {result.get('confidence', 0)}/100")
            print(f"  - Workload Variance: {workload_variance:.2f}")
            
            return result
        except Exception as e:
            return {'error': str(e)}
    
    def _prepare_allocation_summary(self, allocations: List, team_members: List) -> List[Dict]:
        """Prepare allocation data for AI analysis"""
        summary = []
        
        member_task_count = {}
        for alloc in allocations:
            member_name = alloc['team_member']
            if member_name not in member_task_count:
                member_task_count[member_name] = 0
            member_task_count[member_name] += 1
            
            summary.append({
                'task': alloc.get('task_name', 'Unknown'),
                'project': alloc.get('project_name', 'Unknown'),
                'member': member_name,
                'task_number_for_member': member_task_count[member_name],
                'start_week': alloc.get('start_week', 0),
                'duration': alloc.get('end_week', 0) - alloc.get('start_week', 0)
            })
        
        return summary
    
    def _count_consecutive_assignments(self, member_name: str, allocations: List) -> int:
        """Count consecutive assignments for a member"""
        consecutive = 0
        for alloc in reversed(allocations):
            if alloc['team_member'] == member_name:
                consecutive += 1
            else:
                break
        return consecutive
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response, handling both JSON and text formats"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {'raw_response': response, 'parsed': False}
        except Exception as e:
            return {'raw_response': response, 'parse_error': str(e)}


# ============================================================================
# INTEGRATION WITH BACKEND
# ============================================================================

def add_ai_verification_to_analysis(results: Dict, llm) -> Dict:
    """
    Add AI verification to existing analysis results
    
    Args:
        results: Results from multi-agent analysis
        llm: Initialized LLM
        
    Returns:
        Updated results with AI verification
    """
    
    verifier = AIAllocationVerifier(llm)
    
    # Get data from results
    allocations = results.get('portfolio', {}).get('allocations', [])
    team_members = results.get('team_members', [])
    projects = results.get('projects', [])
    
    if not allocations:
        print("⚠️ No allocations found to verify")
        return results
    
    # Run AI verification
    print("\n" + "="*80)
    print("AI-POWERED ALLOCATION VERIFICATION")
    print("="*80)
    
    # Overall verification
    overall_verification = verifier.verify_allocation_logic(
        allocations, team_members, projects
    )
    
    # Scoring weight verification
    weight_verification = verifier.verify_scoring_weights(
        allocations, team_members
    )
    
    # Add to results
    results['ai_verification'] = {
        'overall': overall_verification,
        'weights': weight_verification,
        'timestamp': datetime.now().isoformat()
    }
    
    return results


# ============================================================================
# USAGE EXAMPLE
# ============================================================================
"""
# In backend_integration.py, add after normal analysis:

from ai_allocation_verifier import add_ai_verification_to_analysis

def run_analysis_for_streamlit(team_data, project_data, config, api_key):
    # ... normal analysis ...
    results = run_multi_agent_system(team_data, project_data, config, llm)
    
    # Add AI verification
    results = add_ai_verification_to_analysis(results, llm)
    
    return results
"""

print("✅ AI Allocation Verifier loaded successfully!")
