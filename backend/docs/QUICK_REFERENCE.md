# Menu Image Analysis - Quick Reference

## 🚀 **Quick Start**

```bash
# Test the API is running
curl -X GET "http://localhost:8001/api/v1/menu-image-analysis/supported-formats"

# Extract menu data (no database)
curl -X POST "http://localhost:8001/api/v1/menu-image-analysis/extract-only" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@menu.jpg"

# Extract and save to database  
curl -X POST "http://localhost:8001/api/v1/menu-image-analysis/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@menu.pdf" \
  -F "business_id=your-business-id" \
  -F "auto_create_items=true"
```

## 📋 **Endpoints Summary**

| Endpoint | Method | Purpose | Auth | DB Save |
|----------|--------|---------|------|---------|
| `/extract-only` | POST | Analyze single file | ✅ | ❌ |
| `/bulk-extract-only` | POST | Analyze multiple files | ✅ | ❌ |
| `/analyze` | POST | Analyze + save to DB | ✅ | ✅ |
| `/bulk-analyze` | POST | Bulk analyze + save | ✅ | ✅ |
| `/supported-formats` | GET | Get format info | ❌ | ❌ |

## 📁 **Supported Formats**

- **Images**: JPEG, PNG, WEBP, GIF, BMP (max 20MB)
- **PDFs**: Searchable & scanned (max 50MB, up to 5 pages)

## 🔑 **Required Headers**

```bash
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data
```

## 📊 **Response Structure**

```json
{
  "restaurant_info": { "restaurant_name": "...", "cuisine_type": "..." },
  "menu_items": [
    {
      "name": "Item Name",
      "description": "Description",
      "price": 12.99,
      "category": "main course",
      "allergens": ["dairy", "nuts"],
      "ingredients": ["ingredient1", "ingredient2"],
      "modifiers": [{"type": "size", "options": [...]}],
      "combos": [...],
      "sizes": [...]
    }
  ],
  "total_items": 5,
  "analysis_confidence": 0.9
}
```

## ⚡ **Common Use Cases**

### 1. **Quick Menu Preview**
```bash
# Just extract data for preview
POST /extract-only + image file
```

### 2. **Menu Digitization**  
```bash
# Extract and save to database
POST /analyze + image file + business_id
```

### 3. **Bulk Import**
```bash
# Process multiple menu files
POST /bulk-extract-only + multiple files
```

### 4. **PDF Menu Processing**
```bash
# Upload PDF menu (auto-detects text vs image)
POST /extract-only + PDF file
```

## 🛠 **Environment Setup**

```bash
# Required environment variables
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

## 🐛 **Common Issues**

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Missing/invalid JWT | Check Authorization header |
| 400 Bad Request | Unsupported file type | Use JPEG, PNG, or PDF |
| 413 Payload Too Large | File too big | Max 20MB images, 50MB PDFs |
| 500 Internal Server Error | AWS credentials issue | Check AWS setup |

## 📝 **File Limits**

- **Single Image**: 20MB max
- **Single PDF**: 50MB max  
- **Bulk Upload**: 10 files max per request
- **PDF Pages**: 5 pages max processed

## 🎯 **Quick Test**

```python
import requests

# Test endpoint
response = requests.get("http://localhost:8001/api/v1/menu-image-analysis/supported-formats")
print(response.json())

# Extract menu data
files = {"image": open("menu.jpg", "rb")}
headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.post("http://localhost:8001/api/v1/menu-image-analysis/extract-only", 
                        headers=headers, files=files)
print(f"Found {response.json()['total_items']} menu items")
```

## 📚 **Full Documentation**

- **[Complete Guide](./MENU_IMAGE_ANALYSIS_SUMMARY.md)** - Detailed implementation overview
- **[AWS Setup](./AWS_SETUP_INSTRUCTIONS.md)** - Credential configuration  
- **[PDF Features](./PDF_SUPPORT_UPDATE.md)** - PDF processing capabilities
- **[Demo Scripts](./extract_only_demo.py)** - Python examples