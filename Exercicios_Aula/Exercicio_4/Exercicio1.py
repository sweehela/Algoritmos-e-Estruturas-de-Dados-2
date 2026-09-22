M = 11

filtro = [0] * M

def h1(x):
    return x % 11

def h2(x):
    return (2 * x + 3) % 11

def h3(x):
    return (7 * x + 1) % 11

def inserir_bloom(x):
    filtro[h1(x)] = 1
    filtro[h2(x)] = 1
    filtro[h3(x)] = 1

def verificar_bloom(x):
    posicoes = [h1(x), h2(x), h3(x)]
    bits = [filtro[pos] for pos in posicoes]

    if all(bits):
        return True, posicoes, bits
    else:
        return False, posicoes, bits

inserir_bloom(15)
inserir_bloom(22)
inserir_bloom(45)

print("Vetor final do Filtro de Bloom:")
print(filtro)

resultado, posicoes, bits = verificar_bloom(10)

print("\nID 10:")
print("Posições:", posicoes)
print("Bits:", bits)

if resultado:
    print("Resultado: provavelmente existe.")
else:
    print("Resultado: definitivamente não existe.")


resultado, posicoes, bits = verificar_bloom(22)

print("\nID 22:")
print("Posições:", posicoes)
print("Bits:", bits)

if resultado:
    print("Resultado: provavelmente existe.")
else:
    print("Resultado: definitivamente não existe.")


resultado, posicoes, bits = verificar_bloom(37)

print("\nID 37:")
print("Posições:", posicoes)
print("Bits:", bits)

if resultado:
    print("Resultado: provavelmente existe.")

else:
    print("Resultado: definitivamente não existe.")

# ID 10: possui um bit 0, então não está no filtro.Por isso, o banco de dados não precisa ser consultado, economizando tempo.

# ID 22: possui todos os bits em 1, então provavelmente está no filtro. Como foi inserido, o sistema pode consultar a tabela hash para confirmar.

# ID 37: possui todos os bits em 1, mas não foi inserido. Isso é um falso positivo causado pela colisão dos bits com outros IDs, o bloom filter pode gerar falsos positivos,mas nunca falsos negativos.