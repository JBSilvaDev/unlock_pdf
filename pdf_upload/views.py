from django.shortcuts import render, redirect
from .models import PDFFile
from .forms import PDFUploadForm
from .utils import unlock_pdf, validate_pdf
from django.contrib import messages
from django.utils import timezone
import os
from django.conf import settings

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Valida o arquivo primeiro
            is_valid, error_msg = validate_pdf(request.FILES['file'])
            if not is_valid:
                messages.error(request, error_msg)
                return render(request, 'pdf_upload/upload.html', {'form': form})
            
            try:
                # Salva o arquivo no modelo
                pdf_file = form.save(commit=False)
                
                # Chama a função unlock_pdf com o arquivo enviado (não com o caminho)
                result = unlock_pdf(request.FILES['file'])
                
                # Atualiza o modelo com os resultados
                pdf_file.processed_at = timezone.now()
                pdf_file.is_success = result['status'] == 'success'
                pdf_file.password = result.get('password')
                pdf_file.attempts = result.get('attempts')
                pdf_file.execution_time = result.get('execution_time')
                pdf_file.message = result.get('message')
                
                # Se foi desbloqueado, salva o arquivo resultante
                if result.get('output_path'):
                    unlocked_path = result['output_path']
                    relative_path = os.path.relpath(unlocked_path, settings.MEDIA_ROOT)
                    pdf_file.unlocked_file.name = relative_path
                
                pdf_file.save()
                
                # Mensagem para o usuário
                if pdf_file.is_success:
                    if pdf_file.password:
                        messages.success(request, f"PDF desbloqueado! Senha: {pdf_file.password}")
                    else:
                        messages.success(request, "O PDF não estava protegido por senha.")
                else:
                    messages.warning(request, pdf_file.message)
                
                return render(request, 'pdf_upload/upload.html', {
                    'form': PDFUploadForm(),  # Limpa o formulário
                    'result': result,
                    'pdf_file': pdf_file
                })
                
            except Exception as e:
                messages.error(request, f"Erro ao processar o PDF: {str(e)}")
                return render(request, 'pdf_upload/upload.html', {
                    'form': form,
                    'result': None
                })
    else:
        form = PDFUploadForm()
    
    return render(request, 'pdf_upload/upload.html', {
        'form': form,
        'result': None
    })