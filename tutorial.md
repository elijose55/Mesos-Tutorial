### Tutorial

Para realizar esse tutorial, é necessária uma máquina rodando Ubuntu server, podendo estar rodando na plataforma de sua escolha: AWS, Azure ou VirtualBox na sua própria máquina.
Nesse começo trataremos sobre como criar uma instância na AWS adequada para rodar o Mesos.
#####  Criando instância na AWS EC2
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

#####  Configurando ambiente da Instância
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
#####  Configurando o Mesos
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

#####  Iniciando o zookeeper, mesos-master e mesos-slave

Agora que o ambiente e as variáveis estão todas configuradas, podemos iniciar o processo do mesos-master, mesos-slave e do zookeeper. Para isso, utilize os seguintes comandos:
```sh
$ sudo service zookeeper start
$ sudo service mesos-master start
$ sudo service mesos-slave start
```
Para verificar que tudo está rodando sem erros utilize os seguintes comandos para obter o status dos processos:
```sh
$ sudo service zookeeper status
$ sudo service mesos-master status
$ sudo service mesos-slave status
```

O output deve ser parecido com o mostrado abaixo:
IMAGEM

Quando todos os serviços estiverem rodando corretamente, utilize seu browser e acesse o endereço **[IP_PUBLICO_INSTANCIA]:5050** para entrar no dashboard do mesos, ilustrado abaixo:
**Observação:** Se seu computador estiver conectado a uma rede publica, como de faculdades, esse endereço pode ser bloqueado no browser.
IMAGEM


Como não rodamos nenhum framework ainda, a lista de frameworks estará vazia. 

Para executar um comando simples na infraestrutura recém-criada podemos utilizar a seguinte sintaxe:
```sh
$ mesos-execute --master=<IP_PUBLICO>:5050 --name="echo-test" --command=echo "Hello, World"
```
