from Cryptodome.Cipher import AES
import PyPDF2
import time
import os
from django.conf import settings
import tempfile
import logging

logger = logging.getLogger(__name__)

def unlock_pdf(uploaded_file, digits=4):
    
    """
    Tenta desbloquear um PDF com senha numérica de 1 a 6 dígitos
    """
    start_time = time.time()
    max_attempts = 10 ** digits  # Calcula o máximo de tentativas baseado nos dígitos
    
    result = {
        'status': 'error',
        'password': None,
        'message': f'Testando senhas de {digits} dígitos...',
        'execution_time': 0,
        'attempts': 0,
        'output_path': None,
        'original_filename': uploaded_file.name,
        'digits': digits
    }
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        with open(tmp_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            if not reader.is_encrypted:
                result.update({
                    'status': 'success',
                    'message': 'O PDF não está protegido por senha.',
                    'execution_time': time.time() - start_time
                })
                return result
                
            # Tenta senhas de 0 até 10^digits - 1
            for senha in range(max_attempts):
                senha_tentativa = f"{senha:0{digits}d}"  # Formata com zeros à esquerda
                
                try:
                    if reader.decrypt(senha_tentativa):
                        # Sucesso - gera arquivo desbloqueado
                        output_path = os.path.join(
                            settings.MEDIA_ROOT,
                            'unlocked_pdfs',
                            f'unlocked_{uploaded_file.name}'
                        )
                        
                        writer = PyPDF2.PdfWriter()
                        for pagina in reader.pages:
                            writer.add_page(pagina)
                            
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        result.update({
                            'status': 'success',
                            'password': senha_tentativa,
                            'message': f'PDF desbloqueado! Senha ({digits} dígitos): {senha_tentativa}',
                            'execution_time': time.time() - start_time,
                            'attempts': senha + 1,
                            'output_path': output_path
                        })
                        return result
                        
                except Exception as e:
                    continue
                
                # Feedback a cada 1000 tentativas
                if senha % 1000 == 0 and senha != 0:
                    logger.info(f"Testando... {senha} tentativas realizadas")
            
            # Senha não encontrada
            result.update({
                'message': f'Senha de {digits} dígitos não encontrada.',
                'execution_time': time.time() - start_time,
                'attempts': max_attempts
            })
            
    except Exception as e:
        result['message'] = f"Erro ao processar o PDF: {str(e)}"
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass
    
    return result


def validate_pdf(file):
    """
    Valida se o arquivo é um PDF válido
    Retorna (is_valid, error_message)
    """
    try:
        # Verifica a extensão
        if not file.name.lower().endswith('.pdf'):
            return False, "Apenas arquivos PDF são permitidos."
            
        # Verifica o tamanho (máximo 10MB)
        if file.size > 10 * 1024 * 1024:
            return False, "O arquivo é muito grande (máximo 10MB)."
            
        # Verifica se é um PDF válido (cabeçalho)
        header = file.read(4)
        file.seek(0)
        if header != b'%PDF':
            return False, "O arquivo não parece ser um PDF válido."
            
        return True, ""
        
    except Exception as e:
        return False, f"Erro ao validar o arquivo: {str(e)}"