import PyPDF2
import time

def unlock_pdf(pdf_path, output_path):
    
    for senha in range(100000):
        try:
            
            senha_tentativa = f"{senha:05d}"
            
            with open(pdf_path, 'rb') as pdf_file:
                leitor = PyPDF2.PdfReader(pdf_file)
                
                
                if leitor.is_encrypted:
                    
                    if leitor.decrypt(senha_tentativa):
                        print(f"\nSenha encontrada: {senha_tentativa}")
                        
                        
                        escritor = PyPDF2.PdfWriter()
                        for pagina in leitor.pages:
                            escritor.add_page(pagina)
                            
                        with open(output_path, 'wb') as output_file:
                            escritor.write(output_file)
                            
                        print(f"PDF desbloqueado salvo como: {output_path}")
                        return senha_tentativa
                
                else:
                    print("O PDF não está protegido por senha.")
                    return None
                    
        except Exception as e:
            print(f"Erro ao processar: {e}")
            continue
            
        
        if senha % 1000 == 0 and senha != 0:
            print(f"Testando... {senha} tentativas realizadas")
    
    print("Senha não encontrada (não é um número de 4 dígitos).")
    return None

if __name__ == "__main__":
    print("=== Desbloqueador de PDF ===")
    print("Este programa tenta desbloquear um PDF com senha numérica de até 4 dígitos.")
    
    pdf_protegido = r'Neoenergia Coelba - Fatura Digital.pdf'
    pdf_desbloqueado =r'./novo.pdf'
    
    inicio = time.time()
    senha = unlock_pdf(pdf_protegido, pdf_desbloqueado)
    fim = time.time()
    
    if senha:
        print(f"Processo concluído em {fim - inicio:.2f} segundos.")
        print(f"A senha do PDF era: {senha}")
    else:
        print("Não foi possível desbloquear o PDF com uma senha numérica de 4 dígitos.")