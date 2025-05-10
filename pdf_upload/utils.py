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
    Recebe um arquivo enviado pelo Django e retorna um dicionário com os resultados
    
    Args:
        uploaded_file: InMemoryUploadedFile ou TemporaryUploadedFile do Django
        
    Returns:
        dict: {
            'status': 'success' ou 'error',
            'password': str ou None,
            'message': str,
            'execution_time': float,
            'attempts': int,
            'output_path': str ou None,
            'original_filename': str
        }
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
    
    # Cria diretório para PDFs desbloqueados se não existir
    output_dir = os.path.join(settings.MEDIA_ROOT, 'unlocked_pdfs')
    os.makedirs(output_dir, exist_ok=True)
    
    # Gera nome do arquivo de saída
    original_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
    output_name = f'unlocked_{original_name}.pdf'
    output_path = os.path.join(output_dir, output_name)
    
    # Cria arquivo temporário para processamento
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            # Salva o conteúdo do arquivo enviado no temporário
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Processa o arquivo temporário
        with open(tmp_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Verifica se o PDF está encriptado
            if not reader.is_encrypted:
                result.update({
                    'status': 'success',
                    'message': 'O PDF não está protegido por senha.',
                    'execution_time': time.time() - start_time,
                    'output_path': None  # Não gera arquivo de saída para PDFs não encriptados
                })
                return result
                
            # Tenta senhas de 00000 a 99999
            for senha in range(100000):
                try:
                    senha_tentativa = f"{senha:05d}"
                    
                    if reader.decrypt(senha_tentativa):
                        # PDF desbloqueado com sucesso
                        writer = PyPDF2.PdfWriter()
                        for pagina in reader.pages:
                            writer.add_page(pagina)
                            
                        # Salva o arquivo desbloqueado
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        result.update({
                            'status': 'success',
                            'password': senha_tentativa,
                            'message': 'PDF desbloqueado com sucesso!',
                            'execution_time': time.time() - start_time,
                            'attempts': senha + 1,
                            'output_path': output_path
                        })
                        return result
                        
                except Exception as e:
                    logger.error(f"Erro ao tentar senha {senha_tentativa}: {str(e)}")
                    continue
                
                # Log a cada 1000 tentativas
                if senha % 1000 == 0 and senha != 0:
                    logger.info(f"Testando... {senha} tentativas realizadas")
            
            # Se chegou aqui, não encontrou a senha
            result.update({
                'message': 'Senha não encontrada (não é um número de até 5 dígitos).',
                'execution_time': time.time() - start_time,
                'attempts': 100000
            })
            
    except PyPDF2.PdfReadError as e:
        result['message'] = f"Erro ao ler o PDF: {str(e)}"
        logger.error(f"PdfReadError: {str(e)}")
    except Exception as e:
        result['message'] = f"Erro inesperado: {str(e)}"
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
    finally:
        # Limpeza: remove arquivo temporário
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception as e:
            logger.error(f"Erro ao remover arquivo temporário: {str(e)}")
        
        # Se houve erro, remove o arquivo de saída se existir
        if result['status'] == 'error' and 'output_path' in result and result['output_path']:
            try:
                if os.path.exists(result['output_path']):
                    os.unlink(result['output_path'])
            except Exception as e:
                logger.error(f"Erro ao remover arquivo de saída: {str(e)}")
    
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