### Tutorial

Para realizar esse tutorial, é necessária uma máquina rodando Ubuntu server, podendo estar rodando na plataforma de sua escolha: AWS, Azure ou VirtualBox na sua própria máquina.
Nesse começo trataremos sobre como criar uma instância na AWS adequada para rodar o Mesos.
###### - Criando instância na AWS EC2
1. Realize o login no AWS Console e navegue para a seção do EC2.
2. Clique em **Launch Instance** e selecione a imagem **Ubuntu Server 16.04 LTS AMI (Eligible for Free tier)**.
3. Em **Instance Type** selecione **t2.micro** e continue para **Configure Instance Details**.
4. Selecione para todos os campos a opção **default** e continue para **Add Storage**.
5. Em storage mantenha a opção padrão: **8GB General Purpose SSD**.
6. Adicione uma tag de **Name** na instância para indentifica-lá.
7. Na seção de **Security Groups**, crie um com as portas **22, 2181, 5050** abertas. Caso planeje instalar o Marathon posteriormente, abra a porta 8080 também para acessar o Marathon UI.
8. Por fim, clique em **Review and Launch** e selecione uma key pair (caso já possua uma) ou crie e baixe uma para acessar a instância.
9. Assim que a instância estiver rodando, acesse-a por meio de uma conexão SSH utilizando o **Public IP** e a key pair existente ou criada.
10. Se você estiver usando Windows, será necessário utilizar o Putty para gerar um arquivo .ppk a partir do arquivo baixado .pem e para acessar a instância.
11. Se estiver usando Linux, é possível conectar diretamente do terminal utilizando o arquivo .pem e o endereço IP da instância. Para isso basta utlizar os seguintes comandos:
    ```sh
    $ chmod 400 keypair.pem
    $ ssh –i /dir/da/pem ubuntu@[IP-DA-INSTANCIA]
    ```

###### - Configurando ambiente da Instância
1. Após se conectar a instância, é preciso instalar o Java JDK 8
    ```sh
    $ sudo apt-get update
    $ sudo apt install openjdk-8-jdk openjdk-8-jre
    ```
2. Então, execute os seguintes comandos para adicionar as chaves OpenPGP para o pacote do Mesos. Caso o primeiro comando falhe, tente com o segundo.
    ```sh
    $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv DF7D54CBE56151BF
    OU
    $ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv E56151F
    ```
3. Depois adicione o repositório do Mesos especifico para a versão do Ubuntu sendo utilizada, como estamos utilizando a versão 16.04, seu codinome é **Xenial**, como escrito abaixo.
    ```sh
    $ sudo sh -c 'echo "deb http://repos.mesosphere.com/ubuntu xenial main" >> /etc/apt/sources.list.d/mesosphere.list'
    $ sudo apt-get update
    ```
4. Caso tudo tenha ocorrido bem, podemos agora instalar o Mesos do pacote adicionado.
    ```sh
    $ sudo apt-get -y install mesos
    ```
    Antes de começar a rodar o Mesos é preciso configurar algumas variáveis e arquivos.
###### - Configurando o Mesos
1. Execute o comando:
    ```sh
    $ hostname -f
    ```
    Para obter o hostname da Instância onde o Mesos Master será iniciado.
    
2. Navegue para o diretório: **/etc/zookeeper/conf** e edite o arquivo **zoo.cfg** como mostrado abaixo. Descomente a linha que se inicia com **server.1** e substitua **zookeeper1** com o hostname obtido anteriormente. Como estamos utilizando um zookeeper em um única máquina, podemos substituir por localhost.
    ```sh
    $ cd /etc/zookeeper/conf
    $ sudo nano zoo.cfg
    ```
3. Rode o seguinte comando para editar o arquivo **myid** dentro do diretório **/etc/zookeeper/conf**. Aqui estamos adicionando o número 1 ao arquivo. Esse número é o server id para cada instância zookeeper do cluster, ele não pode ser repetido e varia de 1 a 255.
    ```sh
    $ cd /etc/zookeeper/conf
    $ sudo sh -c 'echo -n "1" >> myid'
    ```
4. Navegue para o diretório: **/etc/mesos** e edite o arquivo **zk** para apontar para o IP interno da instância do zookeeper como mostrado na imagem abaixo, novamente, como estamos utilizando uma única máquina pode-se usar localhost. Caso haja mais de uma instância rodando um mesos-master, o mesmo deverá ser feito em todas. Para clusters com mais de um zookeeper essa propriedade pode ser configurada como:
    ```sh
    zk://10.102.5.183:2181,10.102.5.123:2181,10.102.5.150:2181/mesos
    ```
    ```sh
    $ cd /etc/mesos
    $ sudo nano zk
    ```
    
5. Em seguida, navegue para o diretório: **/etc/mesos-master** e edite o aquivo **quorum** com um valor. Esse valor deve ser definido de uma maneira que 50% do masters devem estar "presentes" para que uma decisão seja tomada. Assim, ele deve ser maior que o número de masters divido por 2, como estamos rodando apenas uma instância com um master, definimos como 1.
    ```sh
    $ cd /etc/mesos-master
    $ sudo nano quorum
    $ cat quorum
    ```

6. Ainda é preciso configurar o hostname e endereco IP para nosso mesos-master. Crie 2 arquivos **ip** e **hostname**, dentro do diretorio **/etc/mesos-master** com os valores corretos.
    ```sh
    $ cd /etc/mesos-master
    $ sudo sh -c 'echo "[IP-INTERNO-DA-INSTANCIA]" >> etc/mesos-master/ip'
    $ sudo sh -c 'echo "[IP-INTERNO-DA-INSTANCIA]" >> hostname'
    $ cat quorum
    ```
    **Observação:** Caso o mesos seja executado em uma subnet privada, utilize o IP Interno da instância para ambos os arquivos. Mas caso esteja em uma subnet pública, utilize o IP público da instância.

###### - Iniciando o zookeeper, mesos-master e mesos-slave
    

    
    
    
    
    
Dillinger requires [Node.js](https://nodejs.org/) v4+ to run.

Install the dependencies and devDependencies and start the server.

```sh
$ cd dillinger
$ npm install -d
$ node app
```

For production environments...

```sh
$ npm install --production
$ NODE_ENV=production node app
```

### Plugins

Dillinger is currently extended with the following plugins. Instructions on how to use them in your own application are linked below.

| Plugin | README |
| ------ | ------ |
| Dropbox | [plugins/dropbox/README.md][PlDb] |
| GitHub | [plugins/github/README.md][PlGh] |
| Google Drive | [plugins/googledrive/README.md][PlGd] |
| OneDrive | [plugins/onedrive/README.md][PlOd] |
| Medium | [plugins/medium/README.md][PlMe] |
| Google Analytics | [plugins/googleanalytics/README.md][PlGa] |


### Development

Want to contribute? Great!

Dillinger uses Gulp + Webpack for fast developing.
Make a change in your file and instantanously see your updates!

Open your favorite Terminal and run these commands.

First Tab:
```sh
$ node app
```

Second Tab:
```sh
$ gulp watch
```

(optional) Third:
```sh
$ karma test
```
#### Building for source
For production release:
```sh
$ gulp build --prod
```
Generating pre-built zip archives for distribution:
```sh
$ gulp build dist --prod
```
### Docker
Dillinger is very easy to install and deploy in a Docker container.

By default, the Docker will expose port 8080, so change this within the Dockerfile if necessary. When ready, simply use the Dockerfile to build the image.

```sh
cd dillinger
docker build -t joemccann/dillinger:${package.json.version} .
```
This will create the dillinger image and pull in the necessary dependencies. Be sure to swap out `${package.json.version}` with the actual version of Dillinger.

Once done, run the Docker image and map the port to whatever you wish on your host. In this example, we simply map port 8000 of the host to port 8080 of the Docker (or whatever port was exposed in the Dockerfile):

```sh
docker run -d -p 8000:8080 --restart="always" <youruser>/dillinger:${package.json.version}
```

Verify the deployment by navigating to your server address in your preferred browser.

```sh
127.0.0.1:8000
```

#### Kubernetes + Google Cloud

See [KUBERNETES.md](https://github.com/joemccann/dillinger/blob/master/KUBERNETES.md)


### Todos

 - Write MORE Tests
 - Add Night Mode

License
----

MIT


**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [dill]: <https://github.com/joemccann/dillinger>
   [git-repo-url]: <https://github.com/joemccann/dillinger.git>
   [john gruber]: <http://daringfireball.net>
   [df1]: <http://daringfireball.net/projects/markdown/>
   [markdown-it]: <https://github.com/markdown-it/markdown-it>
   [Ace Editor]: <http://ace.ajax.org>
   [node.js]: <http://nodejs.org>
   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>
   [jQuery]: <http://jquery.com>
   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>
   [express]: <http://expressjs.com>
   [AngularJS]: <http://angularjs.org>
   [Gulp]: <http://gulpjs.com>

   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>
   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>
   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>
   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>
   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>
   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>
