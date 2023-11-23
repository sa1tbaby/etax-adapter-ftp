from random import randrange as rnd_randrange
from hashlib import sha1 as hash_sha1
from os.path import abspath as os_abspath
from os import system as os_system

doc_count = 15000
doc_random_count = 1525
doc_content = 'please_help_me_they_are_keep_me_in_basement_and_coerce_me_to_write_the_code\n'
doc_size = 1000

type_of_doce = ['RECADV', 'DESADV', 'INBOUND-', 'TEST_']
type_ext = ['.zip', '.txt', '', '.xm', '.xlm', '.xml']
type_marker = '.done'

path = '/FILES_FOR_FTP/'
rnd_letter_pull = 'abcltfghijklmnopqrst'


def print_status(iterate, doc_count):
    if int(int(iterate) % int(doc_count / 10)) == 0:
        status_message = '__________ ~ XX%'

        status = int(int(iterate) // int(doc_count / 100))

        status_message = status_message.replace('_', '#', 1)

        #os_system('cls')

        print(status_message.replace('XX', str(status)))

def rnd_random_doc():
    result = type_of_doce[rnd_randrange(len(type_of_doce))]

    while len(result) < 20:

        match rnd_randrange(2):

            case 0:
                result += rnd_letter_pull[rnd_randrange(20)]

            case 1:
                result += str(rnd_randrange(20))

    return result

for iterate in range(doc_count):

    spawn_type = path
    spawn_type += type_of_doce[rnd_randrange(len(type_of_doce))]
    spawn_type += hash_sha1(bytes(iterate)).hexdigest()
    spawn_type += type_ext[0]

    with open(os_abspath(spawn_type), 'w') as spawned_doc:
        spawned_doc.write(doc_content * doc_size)

    with open(os_abspath(spawn_type + type_marker), 'w') as spawned_doc:
        spawned_doc.write(doc_content * 0)

    print_status(iterate, doc_count)

for iterate in range(doc_random_count):

    spawn_type = path
    spawn_type += rnd_random_doc()
    spawn_type += type_ext[rnd_randrange(5)]

    with open(os_abspath(spawn_type), 'w') as spawned_doc:
        spawned_doc.write(doc_content * rnd_randrange(0, 200, 10))