# AWS Credentials Setup for Amazon Nova

## 🔑 **Required AWS Credentials**

To use Amazon Nova for menu image analysis, you need to update your `.env` file with valid AWS credentials.

### 📝 **Update .env File**

Replace the placeholder values in your `.env` file:

```bash
# Current placeholders (REPLACE THESE):
AWS_ACCESS_KEY_ID=your-aws-access-key-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-key-here
AWS_REGION=us-east-1
```

### 🔧 **How to Get AWS Credentials**

#### **Option 1: AWS IAM User Credentials**
1. Go to AWS Console → IAM → Users
2. Create a new user or select existing user
3. Attach policy: `AmazonBedrockFullAccess`
4. Go to Security Credentials tab
5. Create Access Key
6. Copy the Access Key ID and Secret Access Key

#### **Option 2: AWS CLI Profile**
If you have AWS CLI configured, you can use:
```bash
aws configure list
```

#### **Option 3: Environment Variables**
You can also set these as environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-actual-access-key
export AWS_SECRET_ACCESS_KEY=your-actual-secret-key
export AWS_REGION=us-east-1
```

### 🎯 **Required Permissions**

Your AWS credentials need these permissions:
- `bedrock:InvokeModel` - To call Amazon Nova
- `bedrock:ListFoundationModels` - To list available models

### 🌍 **Supported Regions for Amazon Nova**

Amazon Nova is available in these regions:
- `us-east-1` (N. Virginia) - Default
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)

### 📋 **Example .env Configuration**

```bash
ENVIRONMENT=local
SUPABASE_DB_PASSWORD=appdevmanila
SUPABASE_URL=https://xbtpsheqmlzedeklodqd.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
OPENAI_API_KEY=sk-proj-dnySWMbO2kBPXdYTfxZw...

# AWS Credentials (REPLACE WITH YOUR ACTUAL VALUES)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

### 🔒 **Security Best Practices**

1. **Never commit credentials to git**
2. **Use IAM roles in production**
3. **Rotate access keys regularly**
4. **Use least privilege principle**
5. **Consider AWS Secrets Manager for production**

### 🧪 **Testing Your Setup**

Once you update the credentials, test with:

```bash
# Test AWS connection
aws bedrock list-foundation-models --region us-east-1

# Or test the endpoint
curl -X POST "http://localhost:8001/api/v1/menu-image-analysis/extract-only" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@path/to/menu.jpg"
```

### ❗ **Important Notes**

1. Make sure your AWS account has access to Amazon Nova
2. Some AWS accounts may need to request access to Bedrock models
3. Check AWS Bedrock console for model availability in your region
4. Ensure billing is properly configured for Bedrock usage

### 🚨 **If You Get Permission Errors**

Try these steps:
1. Verify credentials are correct
2. Check IAM permissions
3. Ensure Amazon Nova is available in your region
4. Request model access in Bedrock console if needed