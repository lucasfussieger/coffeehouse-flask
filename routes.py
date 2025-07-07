from flask import Flask, render_template, request, redirect, session, url_for, flash
from classes import user,product,Order, app, db, CartItem, OrderItem
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, login_required, logout_user
import os
import uuid
with app.app_context():
    db.create_all()

@app.route('/', methods = ['GET', 'POST'])
def home():
   if current_user:
      logout_user()
   if request.method == 'POST':
      if request.form['modo'] == 'cadastrar':

        return redirect(url_for('cadastrar'))
      
      return redirect(url_for('entrar'))
   return render_template('home.html')

@app.route('/entrar', methods = ['GET', 'POST'])
def entrar():

   if request.method == 'POST':
      email = request.form['email']
      senha = request.form['senha']

      usuario = user.query.filter_by(email=email).first()

      if usuario and usuario.verificar_senha(senha):
         login_user(usuario)
         return redirect(url_for('store', usuario = current_user))
      else:
         flash('nome de usuário ou senha inválidos',category=Warning)
         return render_template('entrar.html')

   return render_template('entrar.html')

@app.route('/cadastrar', methods = ['GET','POST'])
def cadastrar():
   if request.method == 'POST':       
      nome = str(request.form['nome'])
      email = request.form['email']
      senha = request.form['senha']
      senha_confirmacao = request.form['senha_confirmacao']
      senha_hash = generate_password_hash(senha)
      user_type = request.form['user_type']

      verifi_dados = {
         'nome':nome,
         'email':email,
         'senha':senha,
         'senha de confirmação': senha_confirmacao
      }

      user_exists = user.query.filter_by(email=email).first()
      if user_exists:
          flash('este email já está cadastrado! tente outro!', category=Warning)
          return render_template('cadastro.html')

      for a,b in verifi_dados.items():
         if not b:
            flash(f'{a} vazio, nenhum campo pode ficar vazio', category=Warning)
            return render_template('cadastro.html')
      if senha == senha_confirmacao:
        
         usuario = user(nome=nome,email=email, senha=senha_hash, user_type = user_type)
         db.session.add(usuario)
         db.session.commit()
         login_user(usuario)
         flash(f'bem vindo há CoffeHouse,{current_user.user_type} {current_user.nome} ')
         return redirect(url_for('store', usuario = current_user ))
      else:
         flash('as senhas não batem, a senha de confirmação deve ser igual a senha', category=Warning)
         return render_template('cadastro.html')

   return render_template('cadastro.html')

@app.route('/store', methods = ['GET', 'POST'])
@login_required
def store():
   produtos = db.session.query(product).all()
   return render_template('store.html', produtos=produtos, usuario = current_user )

@app.route('/register_product', methods = ['GET','POST'])
@login_required
def register_product():
   
   if current_user.user_type != 'vendedor':
      flash('você, não tem permissão para acessar essa rota!')
      return redirect(url_for('store'))

   if request.method == 'POST':
         nome = request.form['name']
         preco = request.form['price']
         descricao = request.form['description']
         product_type = request.form['product_type']
         imagem = request.files['image']

         verifi_dados = {
         'nome':nome,
         'preço': preco,
         'descriçâo': descricao,
         'classe do produto': product_type,
         'imagem': imagem
         }

         product_exists = product.query.filter_by(nome=nome).first()
         if product_exists:
            flash('este produto já está cadastrado!', category=Warning)
            return render_template('cadastro.html')

         for a,b in verifi_dados.items():
            if not b:
               flash('nenhum campo pode ficar vazio', category=Warning)
               return redirect(url_for('register_product'))

         if imagem:
            ext = os.path.splitext(imagem.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"

            upload_folder = app.config['UPLOAD_FOLDER']

            os.makedirs(upload_folder, exist_ok=True)

            caminho = os.path.join(upload_folder, filename)
            imagem.save(caminho)
         
         produto = product(
         nome=nome, preco=preco,
         descricao=descricao,
         product_type=product_type,
         image = filename
         )

         db.session.add(produto)
         db.session.commit()
         flash('produto cadastrado com sucesso!')
         return redirect(url_for('store'))

   return render_template('register_product.html', usuario = current_user)

@app.route('/product_details/<int:product_id>', methods = ['GET', 'POST'])
@login_required
def product_details(product_id):
   
   produto = db.session.get(product, product_id)

   if request.method == 'POST':

      if current_user.user_type == 'cliente':
         quantidade = request.form['quantidade']
         existing_item = CartItem.query.filter_by(user_id = current_user.id, product_id=produto.id).first()
         
         verifi_dados = {
         'quantidade': quantidade
         }

         for a,b in verifi_dados.items():
            if not b:
               flash('é necessário uma quantidade para adicionar ao carrinho', category=Warning)
               return redirect(url_for('product_details'))
         if existing_item:
            existing_item.quantity += quantidade
         else:
            new_item = CartItem(
                  product_id=produto.id,
                  product_name=produto.nome,
                  product_price=produto.preco,
                  quantity=quantidade,
                  user_id= current_user.id
            )
            db.session.add(new_item)
         
         db.session.commit()
      flash('produto adicionado ao carrinho, continue comprando!')
      return redirect(url_for('store'))

   return render_template('product_details.html', produto = produto, usuario = current_user)

@app.route('/delete_product/<int:product_id>', methods = ['POST'])
@login_required
def delete_product(product_id):
   
   if current_user.user_type != 'vendedor':
      return 'url indisponivel, apenas usuarios permitidos podem acessar'
   produto = db.session.get(product, product_id)

   db.session.delete(produto)
   db.session.commit()

   return redirect(url_for('store'))

@app.route('/edit_product/<int:product_id>', methods=['GET','POST'])
def edit_product(product_id):
   produto = db.session.get(product, product_id)

   if request.method == 'POST':
      if not produto:
         return "Produto não encontrado", 404
      produto.product_type = request.form['product_type']
      produto.descricao = request.form['descricao']
      produto.nome = request.form['nome']
      produto.preco = request.form['preco']
      imagem = request.files['image']

      verifi_dados = {
         'nome':produto.nome,
         'preço': produto.preco,
         'descriçâo': produto.descricao,
         'classe do produto': produto.product_type,
         'imagem': imagem
         }

      for a,b in verifi_dados.items():
         if not b:
            flash('nenhum campo pode ficar vazio', category=Warning)
            return redirect(url_for('edit_product'))

      if imagem:
            ext = os.path.splitext(imagem.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"

            upload_folder = app.config['UPLOAD_FOLDER']

            os.makedirs(upload_folder, exist_ok=True)

            caminho = os.path.join(upload_folder, filename)
            imagem.save(caminho)

      produto.image = filename

      db.session.commit()
      flash('produto atualizado com sucesso!')
      return redirect(url_for('store'))

   return render_template('edit_product.html', produto=produto, usuario = current_user)

@app.route('/lista_clientes', methods = ['GET','POST'])
def lista_clientes():
   lista = db.session.query(user).filter_by(user_type ='cliente').all()
   if current_user.user_type == 'vendedor':
      return render_template('lista_cliente.html', user = lista, usuario = current_user)
   else:
      return 'url indisponível'

@app.route('/cliente_details/<int:cliente_id>', methods = ['GET', 'POST'])
def cliente_details(cliente_id):
   usuario = db.session.get(user, cliente_id)
   return render_template('cliente_details.html', user = usuario, usuario = current_user)

@app.route('/edit_user/<int:cliente_id>', methods = ['GET', 'POST'])
def edit_user(cliente_id):
   
   if current_user.user_type != 'cliente':
      return 'pagina n disponivel'

   if request.method == 'POST':
      if not user:
         return "usuário não encontrado", 404

      nome = request.form['nome']

      verifi_dados = {
      'nome': nome
      }

      for a,b in verifi_dados.items():
         if not b:
            flash('o nome não pode estar vazio')
            return redirect(url_for('edit_user', cliente_id=cliente_id))
      
      current_user.nome = nome
   
      db.session.commit()

      return redirect(url_for('store'))


   return render_template('edit_user.html', usuario=current_user)



@app.route('/profile_page', methods = ['GET'])
@login_required
def profile_page():
 
   return render_template('profile_page.html', usuario=current_user)

@app.route('/carrinho', methods = ['GET','POST'])
@login_required
def carrinho():
   itens = db.session.query(CartItem).all()
   return render_template('carrinho.html', itens = itens, usuario = current_user)

@app.route('/carrinho/item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item_details(item_id):
    item = CartItem.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        return 403

    if request.method == 'POST':
        if 'delete' in request.form:
            db.session.delete(item)
            db.session.commit()
            flash('Item removido do carrinho.', 'success')
            return redirect(url_for('carrinho'))

        new_quantity = int(request.form.get('quantity', item.quantity))
        if new_quantity <= 0:
            db.session.delete(item)
            flash('Item removido do carrinho.', 'success')
        else:
            item.quantity = new_quantity
            flash('Quantidade atualizada.', 'success')
        
        db.session.commit()
        return redirect(url_for('carrinho'))

    return render_template('pedido_details.html', item=item, usuario = current_user)

@app.route('/deletar_conta', methods=['POST'])
@login_required
def deletar_conta():
    usuario = current_user
    
    # Aqui pode ter lógica para deletar dados associados, se quiser.
    db.session.delete(usuario)
    db.session.commit()
    logout_user()

    flash('Conta deletada com sucesso.')
    return redirect(url_for('home'))




@app.route('/pedido/<int:pedido_id>')
@login_required
def ver_pedido(pedido_id):
    pedido = Order.query.get_or_404(pedido_id)
    return render_template('pedido.html', pedido=pedido, usuario = current_user)

@app.route('/finalizar_carrinho', methods=['POST'])
@login_required
def finalizar_carrinho():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Carrinho vazio.', 'warning')
        return redirect(url_for('carrinho'))

    new_order = Order(user_id=current_user.id, status='pendente')
    db.session.add(new_order)
    db.session.flush()  # Para pegar o ID do pedido já.

    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id = item.product_id,
            quantity = item.quantity
        )
        db.session.add(order_item)
        db.session.delete(item)  # Limpa o carrinho após passar para pedido.

    db.session.commit()
    flash('Pedido criado com sucesso!', 'success')
    return redirect(url_for('store'))


@app.route('/pedidos')
@login_required
def lista_pedidos():
    # Pode ter uma checagem: if not current_user.is_seller: abort(403)
    pedidos = Order.query.all()
    return render_template('lista_pedidos.html', pedidos=pedidos, usuario = current_user)


@app.route('/pedido/<int:pedido_id>/aprovar', methods=['POST'])
@login_required
def aprovar_pedido(pedido_id):
    # Aqui também: checar se current_user é vendedor.
    pedido = Order.query.get_or_404(pedido_id)
    pedido.status = 'aprovado'
    db.session.commit()
    flash('Pedido aprovado.', 'success')
    return redirect(url_for('lista_pedidos'))

@app.route('/store/produtos/<string:product_type>', methods = ['GET','POST'])
def store_filter(product_type):
   produtos = db.session.query(product).filter_by(product_type = product_type).all()
   return render_template('store.html', produtos = produtos, usuario = current_user)
   



if __name__ == "__main__":
    app.run()