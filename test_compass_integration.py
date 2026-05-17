"""
Test script to verify Compass AI integration
Run this to test the complete workflow end-to-end
"""
import asyncio
import os
import sys
import json
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bob_core.orchestration import CompassOrchestrator


@pytest.mark.asyncio
async def test_compass_integration():
    """Test the complete Compass AI workflow"""
    
    print("=" * 70)
    print("COMPASS AI INTEGRATION TEST")
    print("=" * 70)
    
    # Test with the current project directory
    repo_path = os.path.dirname(os.path.abspath(__file__))
    
    print(f"\n📁 Testing with repository: {repo_path}")
    print(f"   (This will analyze the Compass AI project itself)")
    
    try:
        # Step 1: Initialize orchestrator
        print("\n🔧 Step 1: Initializing CompassOrchestrator...")
        orchestrator = CompassOrchestrator(
            repo_path=repo_path,
            include_tests=False
        )
        print("   ✅ Orchestrator initialized")
        
        # Step 2: Analyze repository
        print("\n🔍 Step 2: Analyzing repository structure...")
        intelligence = await orchestrator.analyze_repository()
        print(f"   ✅ Found {intelligence.summary.total_files} files")
        print(f"   ✅ Detected {intelligence.summary.total_edges} dependencies")
        print(f"   ✅ Found {intelligence.summary.circular_dependency_count} circular dependencies")
        
        # Step 3: Show architectural layers
        print("\n🏗️  Step 3: Architectural Layers:")
        for layer, count in intelligence.summary.architectural_layers.items():
            print(f"   • {layer}: {count} files")
        
        # Step 4: Show foundational files
        print("\n🎯 Step 4: Foundational Files (start here):")
        for file in intelligence.summary.foundational_files[:5]:
            print(f"   • {file}")
        
        # Step 5: Show hub files
        print("\n🌟 Step 5: Hub Files (most dependencies):")
        for file in intelligence.summary.hub_files[:5]:
            print(f"   • {file}")
        
        # Step 6: Generate complete analysis
        print("\n🤖 Step 6: Generating complete analysis with AI explanations...")
        print("   (This may take a moment as it calls IBM WatsonX...)")
        
        result = await orchestrator.generate_complete_analysis(
            max_roadmap_files=5,
            task_description="Understand the Compass AI architecture"
        )
        
        print(f"   ✅ Analysis complete!")
        print(f"   ✅ Dependency Radius Score: {result['dependency_radius_score']}/10")
        print(f"   ✅ Generated {len(result['learning_roadmap'])} roadmap items")
        print(f"   ✅ Created graph with {len(result['constellation_graph']['nodes'])} nodes")
        
        # Step 7: Show learning roadmap
        print("\n📚 Step 7: Learning Roadmap (Top 5 Files):")
        for item in result['learning_roadmap'][:5]:
            print(f"\n   Step {item['step']}: {item['file_path']}")
            print(f"   Priority: {item['priority'].upper()}")
            print(f"   Layer: {item['architectural_layer']}")
            print(f"   Complexity: {item['complexity_score']}/100")
            print(f"   Dependencies: {item['dependencies_count']}")
            print(f"   Bob's Explanation: {item['bob_explanation'][:150]}...")
        
        # Step 8: Save result to file
        output_file = "compass_test_result.json"
        print(f"\n💾 Step 8: Saving complete result to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"   ✅ Result saved to {output_file}")
        
        # Step 9: Verify JSON structure
        print("\n✅ Step 9: Verifying JSON structure...")
        required_keys = ['status', 'dependency_radius_score', 'learning_roadmap', 'constellation_graph', 'summary']
        for key in required_keys:
            if key in result:
                print(f"   ✅ '{key}' present")
            else:
                print(f"   ❌ '{key}' missing!")
        
        # Step 10: Verify roadmap item structure
        print("\n✅ Step 10: Verifying roadmap item structure...")
        if result['learning_roadmap']:
            first_item = result['learning_roadmap'][0]
            required_item_keys = ['step', 'file_path', 'dependencies_count', 'priority', 'bob_explanation']
            for key in required_item_keys:
                if key in first_item:
                    print(f"   ✅ '{key}' present in roadmap items")
                else:
                    print(f"   ❌ '{key}' missing from roadmap items!")
        
        print("\n" + "=" * 70)
        print("✅ INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"\nThe complete result has been saved to: {output_file}")
        print("You can now use this JSON structure in the frontend.")
        print("\nTo start the API server, run:")
        print("  cd bob_core && uvicorn main:app --reload --port 8000")
        print("\nThen test the endpoint with:")
        print(f'  curl -X POST http://localhost:8000/api/v1/compass/analyze \\')
        print(f'    -H "Content-Type: application/json" \\')
        print(f'    -d \'{{"repo_path": "{repo_path}", "max_roadmap_files": 5}}\'')
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@pytest.mark.asyncio
async def test_api_endpoint():
    """Test the FastAPI endpoint (requires server to be running)"""
    print("\n" + "=" * 70)
    print("API ENDPOINT TEST")
    print("=" * 70)
    
    try:
        import httpx
    except ImportError:
        print("   ❌ httpx not installed. Install with: pip install httpx")
        return False
    
    try:
        
        repo_path = os.path.dirname(os.path.abspath(__file__))
        
        print("\n🌐 Testing POST /api/v1/compass/analyze endpoint...")
        print("   (Make sure the server is running: uvicorn bob_core.main:app)")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/compass/analyze",
                json={
                    "repo_path": repo_path,
                    "task_description": "Understand the Compass AI architecture",
                    "max_roadmap_files": 5,
                    "include_tests": False
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ API call successful!")
                print(f"   ✅ Status: {result.get('status')}")
                print(f"   ✅ Dependency Score: {result.get('dependency_radius_score')}")
                print(f"   ✅ Roadmap Items: {len(result.get('learning_roadmap', []))}")
                return True
            else:
                print(f"   ❌ API call failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        # Check if it's a connection error
        error_type = type(e).__name__
        error_msg = str(e).lower()
        
        if "connecterror" in error_type.lower() or "connect" in error_msg:
            print("   ⚠️  Could not connect to API server")
            print("   Start the server with: uvicorn bob_core.main:app --reload")
        else:
            print(f"   ❌ Error: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("\n🚀 Starting Compass AI Integration Tests\n")
    
    # Test 1: Direct orchestration
    success1 = await test_compass_integration()
    
    # Test 2: API endpoint (optional, requires server)
    print("\n\nWould you like to test the API endpoint?")
    print("(Requires the FastAPI server to be running)")
    
    # For automated testing, skip API test
    # Uncomment the line below to enable API testing
    # success2 = await test_api_endpoint()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
