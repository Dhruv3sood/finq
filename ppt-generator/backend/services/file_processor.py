from typing import Dict, Tuple

class FileProcessor:
    """Process uploaded files"""
    
    @staticmethod
    def process_files(balance_sheet_file, company_profile_file) -> Tuple[str, str]:
        """
        Read and process uploaded files
        
        Args:
            balance_sheet_file: Flask file object for balance sheet
            company_profile_file: Flask file object for company profile
            
        Returns:
            Tuple of (balance_sheet_text, company_profile_text)
        """
        try:
            balance_sheet_text = balance_sheet_file.read().decode('utf-8')
            company_profile_text = company_profile_file.read().decode('utf-8')
            
            return balance_sheet_text, company_profile_text
        
        except UnicodeDecodeError:
            raise ValueError("Files must be text-based (UTF-8 encoded)")
        except Exception as e:
            raise Exception(f"Error reading files: {str(e)}")
    
    @staticmethod
    def validate_files(balance_sheet_file, company_profile_file) -> Dict:
        """Validate uploaded files"""
        errors = []
        
        if not balance_sheet_file:
            errors.append("Balance sheet file is required")
        
        if not company_profile_file:
            errors.append("Company profile file is required")
        
        # Check file extensions
        if balance_sheet_file and not FileProcessor._allowed_file(balance_sheet_file.filename):
            errors.append("Invalid balance sheet file type")
        
        if company_profile_file and not FileProcessor._allowed_file(company_profile_file.filename):
            errors.append("Invalid company profile file type")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def _allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        from config import Config
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS