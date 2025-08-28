#!/usr/bin/env python3
"""
Deployment script to fix CORS issues by deploying the updated CDK stacks.
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main deployment process."""
    
    print("🏥 CORS Fix Deployment Script")
    print("=" * 50)
    
    # Step 1: Synthesize CDK to check for conflicts
    print("\n📋 Step 1: Checking CDK synthesis...")
    if not run_command("cdk synth", "CDK synthesis check"):
        print("❌ CDK synthesis failed. Please fix the errors above before deploying.")
        sys.exit(1)
    
    # Step 2: Deploy the workflow stack (contains Lambda functions)
    print("\n📋 Step 2: Deploying workflow stack...")
    if not run_command(
        "cdk deploy InsuranceClaimProcessStack/InsuranceClaimProcessWorkflow --require-approval never",
        "Workflow stack deployment"
    ):
        print("❌ Workflow stack deployment failed.")
        sys.exit(1)
    
    # Step 3: Deploy the API stack (references Lambda functions)
    print("\n📋 Step 3: Deploying API stack...")
    if not run_command(
        "cdk deploy InsuranceClaimProcessStack/InsuranceClaimProcessApi --require-approval never",
        "API stack deployment"
    ):
        print("❌ API stack deployment failed.")
        sys.exit(1)
    
    # Step 4: Test the endpoints
    print("\n📋 Step 4: Testing deployment...")
    print("✅ Deployment completed successfully!")
    
    print("\n🎯 Next Steps:")
    print("1. Test your frontend application")
    print("2. Check if CORS issues are resolved")
    print("3. Monitor CloudWatch logs for any errors")
    
    print("\n📋 Available Endpoints:")
    print("- GET /dev/file-proxy?key=<file-key>&bucket=<bucket-name>")
    print("- POST /dev/upload-file (with JSON payload)")
    
    print("\n🔍 Troubleshooting:")
    print("- Check CloudWatch logs if endpoints don't work")
    print("- Verify Lambda functions are deployed correctly")
    print("- Test API Gateway endpoints directly")

if __name__ == "__main__":
    main()