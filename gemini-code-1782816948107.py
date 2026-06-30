import base64
import io
import os
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

# Configuração para salvar as imagens dos produtos enviados
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# O HTML e CSS integrados diretamente no código
HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>AuroraPatas - Pet Shop</title>
    <style>
        /* Cores: Bege (#F5F2EB, #5c4a3c) e Branco (#FFFFFF) */
        body {
            background-color: #F5F2EB;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #4A4A4A;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #ffffff;
            padding: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            display: flex;
            justify-content: center;
        }
        .logo-container {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        /* Logo com as Iniciais A e P */
        .logo-circle {
            background: linear-gradient(135deg, #dfcbb5, #f5f2eb);
            color: #5c4a3c;
            font-size: 24px;
            font-weight: bold;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #5c4a3c;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .brand-name {
            font-size: 26px;
            font-weight: bold;
            color: #5c4a3c;
            letter-spacing: 1px;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 0 20px;
        }
        .card {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.03);
            border: 1px solid #e1dcd6;
        }
        h2 { color: #5c4a3c; margin-top: 0; }
        label { display: block; margin: 15px 0 5px; font-weight: 600; }
        input, select {
            width: 100%; padding: 10px; border: 1px solid #dcd6cd;
            border-radius: 6px; background-color: #faf9f6; box-sizing: border-box;
        }
        .btn {
            background-color: #5c4a3c; color: white; padding: 12px; border: none;
            border-radius: 6px; width: 100%; margin-top: 20px; cursor: pointer;
            font-size: 16px; transition: background 0.3s;
        }
        .btn:hover { background-color: #7a634e; }
        .resultado { margin-top: 20px; text-align: center; padding: 15px; background-color: #fcfbfa; border-radius: 6px; }
    </style>
</head>
<body>

    <header>
        <div class="logo-container">
            <div class="logo-circle">AP</div>
            <span class="brand-name">AuroraPatas</span>
        </div>
    </header>

    <div class="container">
        <section class="card">
            <h2>Adicionar Produto</h2>
            <form action="/salvar-produto" method="POST" enctype="multipart/form-data">
                <label>Nome do Produto:</label>
                <input type="text" name="nome" required>

                <label>Valor (R$):</label>
                <input type="number" id="valor-produto" step="0.01" name="preco" required>

                <label>Imagens do Produto (Selecione exatamente 3):</label>
                <input type="file" name="imagens" accept="image/*" multiple required>

                <button type="submit" class="btn">Cadastrar Produto</button>
            </form>
        </section>

        <section class="card">
            <h2>Realizar Pedido</h2>
            <form id="form-pedido">
                <label>Forma de Pagamento:</label>
                <select id="forma-pagamento" onchange="ajustarOpcoes()">
                    <option value="pix">Pix (QR Code)</option>
                    <option value="especie">Espécie (Dinheiro)</option>
                    <option value="parcelado">Parcelado (Até 4x)</option>
                </select>

                <div id="campo-parcelas" style="display:none;">
                    <label>Quantidade de Parcelas:</label>
                    <select id="parcelas">
                        <option value="1">1x (Sem juros)</option>
                        <option value="2">2x (Sem juros)</option>
                        <option value="3">3x (Sem juros)</option>
                        <option value="4">4x (Sem juros)</option>
                    </select>
                </div>

                <button type="button" onclick="gerarPagamento()" class="btn">Finalizar Pedido</button>
            </form>

            <div id="resultado-pagamento" class="resultado"></div>
        </section>
    </div>

    <script>
        function ajustarOpcoes() {
            const forma = document.getElementById('forma-pagamento').value;
            document.getElementById('campo-parcelas').style.display = (forma === 'parcelado') ? 'block' : 'none';
        }

        async function gerarPagamento() {
            const valor = document.getElementById('valor-produto').value || 0;
            if(valor <= 0) { alert("Por favor, digite o valor no produto primeiro!"); return; }
            
            const forma = document.getElementById('forma-pagamento').value;
            const parcelas = document.getElementById('parcelas').value;

            const response = await fetch(`/processar-pagamento?valor=${valor}&forma=${forma}&parcelas=${parcelas}`);
            const dados = await response.json();

            const div = document.getElementById('resultado-pagamento');
            
            if (forma === 'pix') {
                div.innerHTML = `<h3>Total: R$ ${dados.valor_final}</h3><p>Escaneie para pagar:</p><img src="${dados.qrcode}" width="200">`;
            } else if (forma === 'parcelado') {
                div.innerHTML = `<h3>Pedido Parcelado (${dados.parcelas}x)</h3><p>Valor total: R$ ${dados.valor_final}</p><p>Valor por parcela: <strong>R$ ${dados.valor_parcela}</strong></p>`;
            } else {
                div.innerHTML = `<h3>Pedido em Espécie</h3><p>Total a pagar em dinheiro: R$ ${dados.valor_final}</p>`;
            }
        }
    </script>
</body>
</html>
"""

# Rota Principal: Carrega a página web
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

# Rota para receber o cadastro do produto e guardar as 3 imagens
@app.route('/salvar-produto', methods=['POST'])
def salvar_produto():
    nome = request.form.get('nome')
    preco = request.form.get('preco')
    imagens = request.files.getlist('imagens')

    if len(imagens) > 3:
        return "Erro: Você enviou mais do que 3 imagens!", 400

    for img in imagens:
        if img.filename:
            img.save(os.path.join(UPLOAD_FOLDER, img.filename))

    return f"<h3>Produto '{nome}' cadastrado com sucesso!</h3><p>Valor: R$ {preco}</p><p>As 3 imagens foram recebidas e salvas no servidor.</p><br><a href='/'>Voltar</a>"

# Rota da API para gerar o QR Code Pix ou calcular as Parcelas
@app.route('/processar-pagamento', methods=['GET'])
def processar_pagamento():
    import qrcode  # Importado aqui para garantir o funcionamento interno
    valor = float(request.args.get('valor', 0.0))
    forma = request.args.get('forma', 'pix')
    parcelas = int(request.args.get('parcelas', 1))

    resposta = {"valor_final": f"{valor:.2f}"}

    if forma == 'pix':
        # Cria uma string fictícia no padrão Pix BR Code utilizando o valor da compra
        dados_pix = f"00020101021126360014br.gov.bcb.pix0114suachavepix5204000053039865405{valor:.2f}5802BR5912AuroraPatas6009SaoPaulo62070503***6304"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(dados_pix)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#5c4a3c", back_color="white") # QR code nas cores do site
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        resposta["qrcode"] = f"data:image/png;base64,{img_str}"

    elif forma == 'parcelado':
        valor_parcela = valor / parcelas
        resposta["valor_parcela"] = f"{valor_parcela:.2f}"
        resposta["parcelas"] = parcelas

    return jsonify(resposta)

if __name__ == '__main__':
    app.run(port=5000, debug=True)