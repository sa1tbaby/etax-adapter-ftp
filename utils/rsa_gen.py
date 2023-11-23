import rsa
import os.path
from cryptography.fernet import Fernet
from json import load

class Cypher:

    pub_key = None
    priv_key = None
    aes_key = None

    def generate_keys(self) -> None:
        """
        * pub_key=Публичный ключ RSA
        * priv_key=Приватный ключ RSA
        * aes_key=Симметричный ключ, файл ключа сохраняется в зашифрованном, методом RSA, виде

        :return: None
        """

        #Генерация асимметричных ключей
        (self.pub_key, self.priv_key) = rsa.newkeys(2048)

        pub_key_pem = self.pub_key.save_pkcs1(format='PEM')
        priv_key_pem = self.priv_key.save_pkcs1(format='PEM')

        aes_key_decrypt = Fernet.generate_key()
        self.aes_key = rsa.encrypt(message=aes_key_decrypt, pub_key=self.pub_key)

        with open(os.path.join(input('укажите dir для сохранения симметричного ключа: '),
                               'aes_key.key'),
                  'wb') as key:

            key.write(self.aes_key)

        with open(os.path.join(input('укажите dir для сохранения публичного ключа: '),
                               'pub_key.PEM'),
                  'wb') as key:

            key.write(pub_key_pem)

        with open(os.path.join(input('укажите dir для сохранения приватного ключа: '),
                               'priv_key.PEM'),
                  'wb') as key:

            key.write(priv_key_pem)

    def load_key(self, mode: str, direrctory: str) -> True | False:
        """
        * mode='pub' Загрузка публичного ключа RSA формат PEM
        * mode='priv' Загрузка приватного ключа RSA формат PEM
        * mode='aes' Загрузка симметричного ключа  формат key

        :param mode: str
        :param direrctory: str
        :return: True | False
        """

        match mode:

            case 'pub':

                with open(os.path.join(direrctory, 'pub_key.PEM'), 'rb') as pub_file:
                    self.pub_key = rsa.PublicKey.load_pkcs1(keyfile=pub_file.read(),
                                                            format='PEM')

                    return True

            case 'priv':

                with open(os.path.join(direrctory, 'priv_key.PEM'), 'rb') as priv_file:
                    self.priv_key = rsa.PrivateKey.load_pkcs1(keyfile=priv_file.read(),
                                                             format='PEM')

                    return True

            case 'aes':

                if self.priv_key is not None:

                    with open(os.path.join(direrctory, 'aes_key.key'), 'rb') as aes_file_encrypt:
                        self.aes_key = aes_file_encrypt.read()

                    return True

                else:

                    return False

    def load_keys(self, direrctory: str):

        tmp_mes = {'pub': False, 'priv': False, 'aes': False}

        if self.load_key(mode='pub', direrctory='app/configs'):
            tmp_mes['pub'] = True

        if self.load_key(mode='priv', direrctory='app/configs'):
            tmp_mes['priv'] = True

        if self.load_key(mode='aes', direrctory='app/configs'):
            tmp_mes['aes'] = True

        return tmp_mes

    def decrypt(self, message):

        if self.aes_key is not None:

            cypher = Fernet(rsa.decrypt(crypto=self.aes_key,
                                        priv_key=self.priv_key)
                            )

            return cypher.decrypt(message)

        else:

            return False

    def encrypt(self, message):

        if self.aes_key is not None:

            cypher = Fernet(rsa.decrypt(crypto=self.aes_key,
                                        priv_key=self.priv_key))

            return cypher.encrypt(message)

        else:

            return False

if __name__ == "__main__":

    pass