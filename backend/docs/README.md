# Menu Image Analysis - Documentation

This directory contains comprehensive documentation for the Menu Image Analysis system built with AWS Bedrock and Amazon Nova.

## 📚 **Documentation Index**

### 🚀 **Quick Start**
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Essential commands and API quick reference
- **[MENU_IMAGE_ANALYSIS_SUMMARY.md](./MENU_IMAGE_ANALYSIS_SUMMARY.md)** - Complete implementation overview and API reference

### 🔧 **Setup & Configuration**
- **[AWS_SETUP_INSTRUCTIONS.md](./AWS_SETUP_INSTRUCTIONS.md)** - AWS Bedrock credentials setup guide
- **[LIMITED_ACCESS_SOLUTION.md](./LIMITED_ACCESS_SOLUTION.md)** - OpenAI fallback for limited AWS access

### 📈 **Updates & Features**
- **[AMAZON_NOVA_UPDATE.md](./AMAZON_NOVA_UPDATE.md)** - Migration from Claude to Amazon Nova
- **[PDF_SUPPORT_UPDATE.md](./PDF_SUPPORT_UPDATE.md)** - PDF processing capabilities

### 🧪 **Testing & Examples**
- **[extract_only_demo.py](./extract_only_demo.py)** - Python demo script for testing endpoints

## 🎯 **System Overview**

The Menu Image Analysis system is a comprehensive solution that extracts structured menu data from images and PDFs using Amazon Nova via AWS Bedrock.

### ✨ **Key Features**

- **Multi-format Support**: Images (JPEG, PNG, WEBP, GIF, BMP) and PDFs
- **Comprehensive Extraction**: Menu items, prices, categories, allergens, ingredients, modifiers, combos, sizes
- **Dual Processing**: Extract-only endpoints and database integration
- **Bulk Processing**: Handle multiple files simultaneously
- **Smart PDF Handling**: Text extraction + image conversion fallback
- **Multi-page Support**: Process up to 5 PDF pages

### 🔗 **API Endpoints**

#### **Extract-Only (No Database)**
- `POST /api/v1/menu-image-analysis/extract-only` - Single file analysis
- `POST /api/v1/menu-image-analysis/bulk-extract-only` - Multiple files analysis

#### **Database Integration**
- `POST /api/v1/menu-image-analysis/analyze` - Single file + database upload
- `POST /api/v1/menu-image-analysis/bulk-analyze` - Multiple files + database upload

#### **Utility**
- `GET /api/v1/menu-image-analysis/supported-formats` - Get supported formats and limits

### 📊 **Response Format**

```json
{
  "restaurant_info": {
    "restaurant_name": "Restaurant Name",
    "cuisine_type": "Italian"
  },
  "menu_items": [
    {
      "name": "Margherita Pizza",
      "description": "Fresh tomatoes, mozzarella, basil",
      "price": 16.99,
      "category": "main course",
      "allergens": ["dairy", "gluten"],
      "ingredients": ["tomatoes", "mozzarella", "basil"],
      "modifiers": [
        {
          "type": "size",
          "options": [
            {"name": "Small", "price": 0},
            {"name": "Large", "price": 4.00}
          ]
        }
      ],
      "combos": [],
      "sizes": [
        {"name": "Small", "price": 16.99},
        {"name": "Large", "price": 20.99}
      ]
    }
  ],
  "total_items": 1,
  "analysis_confidence": 0.9
}
```

### 🔐 **Authentication**

All endpoints require authentication via Bearer token:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

### 📏 **File Limits**

- **Images**: Maximum 20MB per file
- **PDFs**: Maximum 50MB per file
- **Bulk Processing**: Maximum 10 files per request
- **PDF Pages**: Maximum 5 pages processed per PDF

### �� **Technology Stack**

- **AI Model**: Amazon Nova Pro via AWS Bedrock
- **Framework**: FastAPI (Python)
- **Image Processing**: PIL (Pillow)
- **PDF Processing**: PyPDF2 + pdf2image
- **Authentication**: JWT tokens
- **Database**: Supabase (optional integration)

### 🚀 **Getting Started**

1. **Setup AWS Credentials** - Follow [AWS_SETUP_INSTRUCTIONS.md](./AWS_SETUP_INSTRUCTIONS.md)
2. **Review API Reference** - Check [MENU_IMAGE_ANALYSIS_SUMMARY.md](./MENU_IMAGE_ANALYSIS_SUMMARY.md)
3. **Test Endpoints** - Use [extract_only_demo.py](./extract_only_demo.py)
4. **Upload Files** - Start with `/extract-only` endpoint for testing

### 💡 **Use Cases**

- **Restaurant Onboarding**: Quick menu digitization
- **Menu Updates**: Extract data from new menu versions
- **Data Migration**: Convert PDF menus to structured data
- **Quality Assurance**: Validate menu information
- **Integration**: Connect with POS systems and ordering platforms

### 🆘 **Support**

For technical issues or questions:
1. Check the relevant documentation file
2. Review error messages in server logs
3. Verify AWS credentials and permissions
4. Test with supported file formats

---

**Built with ❤️ using Amazon Nova and AWS Bedrock**

---

# Tably Backend Documentation

This directory contains documentation for the Tably backend API and related components.

## API Documentation

### [API Overview](./API_OVERVIEW.md)
Complete overview of all API endpoints in the system, including:
- Authentication endpoints
- Menu items endpoints
- Orders endpoints
- Common response formats
- HTTP status codes
- Pagination and filtering

### [Orders API](./ORDERS_API.md)
Detailed documentation for the Orders API endpoints, including:
- Authentication requirements
- Endpoint descriptions and examples
- Request/response schemas
- Role-based access control
- Error handling
- Database schema

### Menu Items API
Documentation for the Menu Items API (to be added)

### Auth API
Documentation for the Authentication API (to be added)

## Database Schema

### [Orders Schema](../sql/orders_schema.sql)
SQL schema for the orders and order_items tables including:
- Table definitions
- Foreign key relationships
- Row Level Security (RLS) policies
- Indexes for performance
- Triggers for automatic updates

### [Main Schema](../sql/schema.sql)
Main database schema for the application

## Development

### [Development Guide](./DEVELOPMENT_GUIDE.md)
Comprehensive guide for developing and maintaining the API, including:
- Project structure overview
- Step-by-step guide for adding new endpoints
- Best practices for authentication, error handling, and database operations
- Testing strategies
- Deployment instructions
- Security considerations

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables
3. Run database migrations
4. Start the development server

### Testing
- API endpoints can be tested using the interactive docs at `/docs`
- Use the provided example requests in the API documentation

### Deployment
- Docker configuration available in `Dockerfile`
- Docker Compose setup in `docker-compose.yml`

## Contributing

When adding new API endpoints:
1. Create models in `app/models/`
2. Create database connection in `app/db/`
3. Create endpoints in `app/api/endpoints/`
4. Update this documentation
5. Add SQL schema if needed 
