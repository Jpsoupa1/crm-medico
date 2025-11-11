// assets/js/scripts.js
document.addEventListener('DOMContentLoaded', function() {
    
    // ========== MÁSCARA CPF ==========
    const cpfInput = document.getElementById('id_cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 11) {
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d)/, '$1.$2');
                value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
                e.target.value = value;
            }
        });
    }
    
    // ========== MÁSCARA TELEFONE ==========
    const telefoneInput = document.getElementById('id_telefone');
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 11) {
                value = value.replace(/^(\d{2})(\d)/g, '($1) $2');
                value = value.replace(/(\d)(\d{4})$/, '$1-$2');
                e.target.value = value;
            }
        });
    }
    
    // ========== MÁSCARA CEP ==========
    const cepInput = document.getElementById('id_cep');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length <= 8) {
                value = value.replace(/^(\d{5})(\d)/, '$1-$2');
                e.target.value = value;
            }
        });
    }
    
    // ========== APENAS LETRAS NO NOME ==========
    const nomeInput = document.getElementById('id_nome_completo');
    if (nomeInput) {
        nomeInput.addEventListener('input', function(e) {
            // Remove números e caracteres especiais, mantém letras e espaços
            e.target.value = e.target.value.replace(/[^A-Za-zÀ-ÿ\s]/g, '');
        });
    }
    
    // ========== BUSCAR CEP (API ViaCEP) ==========
    const btnBuscarCep = document.getElementById('btn-buscar-cep');
    const cepLoading = document.getElementById('cep-loading');
    const enderecoInput = document.getElementById('id_endereco');
    const cidadeInput = document.getElementById('id_cidade');
    const estadoInput = document.getElementById('id_estado');
    
    if (btnBuscarCep) {
        btnBuscarCep.addEventListener('click', async function() {
            const cep = cepInput.value.replace(/\D/g, '');
            
            if (cep.length !== 8) {
                alert('Por favor, digite um CEP válido com 8 dígitos.');
                return;
            }
            
            // Mostrar loading
            cepLoading.style.display = 'block';
            btnBuscarCep.disabled = true;
            
            try {
                const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
                const data = await response.json();
                
                if (data.erro) {
                    alert('CEP não encontrado. Por favor, verifique o número digitado.');
                } else {
                    // Preencher campos
                    enderecoInput.value = data.logradouro || '';
                    cidadeInput.value = data.localidade || '';
                    estadoInput.value = data.uf || '';
                    
                    // Focar no campo de número (se houver)
                    // endereço, sem número, então foca em endereço para completar o número
                    enderecoInput.focus();
                }
            } catch (error) {
                alert('Erro ao buscar CEP. Verifique sua conexão com a internet.');
                console.error('Erro:', error);
            } finally {
                // Esconder loading
                cepLoading.style.display = 'none';
                btnBuscarCep.disabled = false;
            }
        });
        
        // Buscar automaticamente ao pressionar Enter no campo CEP
        cepInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                btnBuscarCep.click();
            }
        });
    }
});