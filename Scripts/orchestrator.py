#!/usr/bin/env python3
"""
OpenAPI Documentation Generator - Orchestrator

This script coordinates multiple Claude Code agents to generate comprehensive
API documentation from an OpenAPI specification.

Architecture:
1. Parser Agent - extracts endpoint data from OpenAPI spec
2. Parallel execution per endpoint:
   - Parameter Documenter Agent - creates API reference docs
   - Example Generator Agent - creates realistic examples
   - How-To Guide Agent - creates tutorial-style guides
3. Sequential final steps:
   - Glossary Agent - builds comprehensive glossary
   - TOC Agent - creates table of contents

Demonstrates:
- Multi-agent coordination
- Parallel agent execution for efficiency
- Error handling and validation
- Context management across agents
"""

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any
import yaml


class DocumentationOrchestrator:
    """Coordinates agents to generate API documentation from OpenAPI specs."""
    
    def __init__(self, spec_path: str, output_dir: str = "output"):
        self.spec_path = Path(spec_path)
        self.output_dir = Path(output_dir)
        self.parsed_dir = self.output_dir / "parsed"
        self.endpoints_dir = self.output_dir / "endpoints"
        
        # Create output directories
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        self.endpoints_dir.mkdir(parents=True, exist_ok=True)
        
        # Track processed endpoints
        self.endpoints: List[Dict[str, Any]] = []
        self.errors: List[str] = []
    
    def run_agent(self, agent_name: str, input_data: str = None, 
                  timeout: int = 300) -> Dict[str, Any]:
        """
        Run a Claude Code agent using the Task tool.
        
        Args:
            agent_name: Name of the agent (filename without .md)
            input_data: Optional input to pass to the agent
            timeout: Timeout in seconds
            
        Returns:
            Dict with 'success', 'output', and optional 'error'
        """
        try:
            # In a real Claude Code environment, this would use the Task tool
            # For demonstration, we'll simulate the agent execution
            
            print(f"🤖 Running {agent_name} agent...")
            
            # Simulate agent execution with subprocess calling claude command
            # In actual usage: Use Task tool to spawn subagent
            cmd = f"# claude task --agent .claude/agents/{agent_name}.md"
            
            if input_data:
                cmd += f" --input '{input_data}'"
            
            print(f"   Command: {cmd}")
            
            # For this demonstration, we'll create a marker file
            marker = self.output_dir / f".{agent_name}.completed"
            marker.touch()
            
            return {
                "success": True,
                "output": f"Agent {agent_name} completed successfully",
                "agent": agent_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": agent_name
            }
    
    def validate_openapi_spec(self) -> bool:
        """Validate the OpenAPI specification before processing."""
        print("📋 Validating OpenAPI specification...")
        
        if not self.spec_path.exists():
            self.errors.append(f"Spec file not found: {self.spec_path}")
            return False
        
        try:
            with open(self.spec_path, 'r') as f:
                spec = yaml.safe_load(f)
            
            # Validate required fields
            if 'openapi' not in spec:
                self.errors.append("Missing 'openapi' version field")
                return False
            
            if not spec['openapi'].startswith('3.'):
                self.errors.append(f"Unsupported OpenAPI version: {spec['openapi']}")
                return False
            
            if 'paths' not in spec:
                self.errors.append("Missing 'paths' section")
                return False
            
            if 'info' not in spec:
                self.errors.append("Missing 'info' section")
                return False
            
            print(f"   ✓ Valid OpenAPI {spec['openapi']} specification")
            print(f"   ✓ API: {spec['info'].get('title', 'Unknown')}")
            print(f"   ✓ Found {len(spec['paths'])} endpoint paths")
            
            return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Validation error: {e}")
            return False
    
    def extract_endpoints(self) -> List[Dict[str, str]]:
        """Extract endpoint information from the spec."""
        print("\n📊 Extracting endpoints from specification...")
        
        with open(self.spec_path, 'r') as f:
            spec = yaml.safe_load(f)
        
        endpoints = []
        for path, methods in spec['paths'].items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    endpoint_id = self.generate_endpoint_id(method, path)
                    endpoints.append({
                        'id': endpoint_id,
                        'method': method.upper(),
                        'path': path,
                        'operation_id': details.get('operationId', endpoint_id)
                    })
                    print(f"   • {method.upper()} {path} → {endpoint_id}")
        
        return endpoints
    
    @staticmethod
    def generate_endpoint_id(method: str, path: str) -> str:
        """Generate a filesystem-safe endpoint ID."""
        # Convert /pets/{id} to get-pets-by-id
        clean_path = path.strip('/')
        clean_path = clean_path.replace('{', 'by-').replace('}', '')
        clean_path = clean_path.replace('/', '-')
        return f"{method.lower()}-{clean_path}"
    
    def phase_1_parse(self) -> bool:
        """Phase 1: Run parser agent to extract endpoint data."""
        print("\n" + "="*60)
        print("PHASE 1: Parsing OpenAPI Specification")
        print("="*60)
        
        result = self.run_agent('openapi-parser', str(self.spec_path))
        
        if not result['success']:
            self.errors.append(f"Parser failed: {result.get('error')}")
            return False
        
        print("   ✓ Parsing complete")
        return True
    
    def phase_2_document_endpoints(self, endpoints: List[Dict[str, str]]) -> bool:
        """Phase 2: Generate documentation for each endpoint in parallel."""
        print("\n" + "="*60)
        print("PHASE 2: Generating Endpoint Documentation (Parallel)")
        print("="*60)
        
        # Use ThreadPoolExecutor for parallel agent execution
        max_workers = min(4, len(endpoints))  # Limit concurrent agents
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all endpoint documentation tasks
            futures = {}
            
            for endpoint in endpoints:
                # For each endpoint, run three agents in parallel
                param_future = executor.submit(
                    self.run_agent, 
                    'parameter-documenter',
                    endpoint['id']
                )
                futures[param_future] = f"Parameter docs for {endpoint['id']}"
                
                example_future = executor.submit(
                    self.run_agent,
                    'example-generator',
                    endpoint['id']
                )
                futures[example_future] = f"Examples for {endpoint['id']}"
                
                howto_future = executor.submit(
                    self.run_agent,
                    'howto-generator',
                    endpoint['id']
                )
                futures[howto_future] = f"How-to for {endpoint['id']}"
            
            # Wait for all to complete and check results
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    result = future.result()
                    if result['success']:
                        print(f"   ✓ {task_name}")
                    else:
                        error_msg = f"{task_name} failed: {result.get('error')}"
                        self.errors.append(error_msg)
                        print(f"   ✗ {error_msg}")
                except Exception as e:
                    error_msg = f"{task_name} exception: {str(e)}"
                    self.errors.append(error_msg)
                    print(f"   ✗ {error_msg}")
        
        return len(self.errors) == 0
    
    def phase_3_build_glossary(self) -> bool:
        """Phase 3: Build glossary from all reference docs."""
        print("\n" + "="*60)
        print("PHASE 3: Building Glossary")
        print("="*60)
        
        result = self.run_agent('glossary-builder')
        
        if not result['success']:
            self.errors.append(f"Glossary generation failed: {result.get('error')}")
            return False
        
        print("   ✓ Glossary complete")
        return True
    
    def phase_4_generate_toc(self) -> bool:
        """Phase 4: Generate table of contents."""
        print("\n" + "="*60)
        print("PHASE 4: Generating Table of Contents")
        print("="*60)
        
        result = self.run_agent('toc-generator')
        
        if not result['success']:
            self.errors.append(f"TOC generation failed: {result.get('error')}")
            return False
        
        print("   ✓ Table of contents complete")
        return True
    
    def run(self) -> bool:
        """Execute the complete documentation generation workflow."""
        print("\n" + "="*60)
        print("OpenAPI Documentation Generator")
        print("="*60)
        print(f"Spec: {self.spec_path}")
        print(f"Output: {self.output_dir}")
        
        # Validate spec
        if not self.validate_openapi_spec():
            return False
        
        # Extract endpoint list
        endpoints = self.extract_endpoints()
        if not endpoints:
            self.errors.append("No endpoints found in specification")
            return False
        
        # Phase 1: Parse
        if not self.phase_1_parse():
            return False
        
        # Phase 2: Generate endpoint documentation (parallel)
        if not self.phase_2_document_endpoints(endpoints):
            print("\n⚠️  Some endpoint documentation failed, but continuing...")
        
        # Phase 3: Build glossary
        if not self.phase_3_build_glossary():
            return False
        
        # Phase 4: Generate TOC
        if not self.phase_4_generate_toc():
            return False
        
        return True
    
    def print_summary(self):
        """Print execution summary."""
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"❌ Completed with {len(self.errors)} errors:")
            for error in self.errors:
                print(f"   • {error}")
        else:
            print("✅ Documentation generation completed successfully!")
        
        print(f"\nOutput location: {self.output_dir.absolute()}")
        print("\nGenerated files:")
        print(f"   • Table of Contents: {self.output_dir}/toc.md")
        print(f"   • Glossary: {self.output_dir}/glossary.md")
        print(f"   • Endpoint docs: {self.endpoints_dir}/")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <openapi-spec.yaml>")
        sys.exit(1)
    
    spec_path = sys.argv[1]
    
    orchestrator = DocumentationOrchestrator(spec_path)
    success = orchestrator.run()
    orchestrator.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
