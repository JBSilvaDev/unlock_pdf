from django.shortcuts import render, redirect
from .forms import PDFUploadForm
from .utils import unlock_pdf, validate_pdf
from django.contrib import messages
from django.utils import timezone
import os
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def upload_pdf(request):

    if 'processed_data' in request.session:
        del request.session['processed_data']
        
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Valida o arquivo primeiro
            is_valid, error_msg = validate_pdf(request.FILES['file'])
            if not is_valid:
                messages.error(request, error_msg)
                return render(request, 'pdf_upload/upload.html', {'form': form})
            
            try:
                pdf_file = form.save(commit=False)
                digits = form.cleaned_data['digits']
                
                # Chama a função unlock_pdf com o arquivo e número de dígitos
                result = unlock_pdf(request.FILES['file'], digits)
                
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
                if result['status'] == 'success':
                    if result.get('password'):
                        messages.success(request, f"PDF desbloqueado! Senha de {result['digits']} dígitos: {result['password']}")
                    else:
                        messages.success(request, result['message'])
                else:
                    messages.error(request, result['message'])
                
                return render(request, 'pdf_upload/upload.html', {
                    'form': PDFUploadForm(),  # Limpa o formulário
                    'result': result,
                    'pdf_file': pdf_file
                })
                
            except Exception as e:
                messages.error(request, f"Erro ao processar o PDF: {str(e)}")
                return render(request, 'pdf_upload/upload.html', {
                    'form': form,
                    'result': request.session.pop('processed_data', None)
                })
    else:
        form = PDFUploadForm()
    
    return render(request, 'pdf_upload/upload.html', {
        'form': form,
        'result': None
    })