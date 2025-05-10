from Cryptodome.Cipher import AES
import PyPDF2
import time
import os
from django.conf import settings
import tempfile
import logging

logger = logging.getLogger(__name__)

def unlock_pdf(uploaded_file):
    """
    Tenta desbloquear um PDF com senha numérica de até 5 dígitos
    """
    start_time = time.time()
    result = {
        'status': 'error',
        'password': None,
        'message': 'Erro desconhecido',
        'execution_time': 0,
        'attempts': 0,
        'output_path': None,
        'original_filename': uploaded_file.name
    }
    
    try:
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Processa o PDF
        with open(tmp_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            if not reader.is_encrypted:
                result.update({
                    'status': 'success',
                    'message': 'O PDF não está protegido por senha.',
                    'execution_time': time.time() - start_time
                })
                return result
                
            for senha in range(100000):
                senha_tentativa = f"{senha:05d}"
                try:
                    if reader.decrypt(senha_tentativa):
                        # Sucesso - atualiza o resultado
                        result.update({
                            'status': 'success',
                            'password': senha_tentativa,
                            'message': f'PDF desbloqueado! Senha: {senha_tentativa}',
                            'execution_time': time.time() - start_time,
                            'attempts': senha + 1
                        })
                        return result
                        
                except Exception as e:
                    # Ignora erros de senha individual e continua
                    continue
                
    except Exception as e:
        result['message'] = f"Erro ao processar o PDF: {str(e)}"
    finally:
        # Limpeza do arquivo temporário
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