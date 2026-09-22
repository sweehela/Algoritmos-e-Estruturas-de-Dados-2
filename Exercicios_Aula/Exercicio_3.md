1) 1. Você está projetando o índice de um banco de dados usando uma Árvore B. Sabe-se que o disco rígido do servidor realiza leituras em blocos de 4096 bytes (4KB). Cada nó da sua árvore deve caber perfeitamente em um bloco de disco. Sabe-se que:
 - Cada ponteiro para um filho ocupa 4 bytes.
 - Cada chave de busca ocupa 8 bytes.
a. Calcule a Ordem (M) ideal para esta árvore B. (Dica: Monte a equação considerando o número máximo de ponteiros M e o número máximo de chaves).
R:  ponteiro + chaves <= 4096
    4M + 8(M-1) <= 4096
    12M - 8 <= 4096
    12M <= 4104
    M = 342

    verificação:
    342(4) + 341(8) = 1368 + 2728 = 4096

b. Com a Ordem calculada, responda: qual é o número mínimo e máximo de chaves que um nó intermediário pode conter?
R:  M = 342
    M - 1 = 342 - 1 = 341 chaves
    342/2 = 171 - 1 = 170 chaves

    portanto, o máximo de chaves é de 341 e o mínimo de chaves é de 170.


c. Se a raiz do seu índice atingir a lotação máxima e receber uma nova inserção, explique tecnicamente o que acontecerá com ela e com a altura geral da árvore.
R: A raiz é dividida em dois nós e uma chave do meio é promovida para uma nova raiz, consequentemente a altura da árvore aumenta em 1.

2. Considere uma árvore B de ordem 𝑀=4. Realize as seguintes operações:
a. Insira os números na seguinte ordem: 10, 20, 5, 6, 15, 30, 25, 35, 2, 1, 8, 40. Represente visualmente a árvore B gerada após todas as inserções.
R:                         [20]          -> imagina que ta simétrico
                    /                 \
                [5 | 10]             [30]
            /      |      \         /     \
        [1 | 2]  [6 | 8]  [15]  [25]   [35 | 40]


b. A partir da árvore resultante, remova o número 25. Mostre o estado da árvore.
R:                          [20]          
                    /                 \
                [5 | 10]             [35]
            /      |      \         /     \
        [1 | 2]  [6 | 8]  [15]    [30]   [40]

c. A partir do resultado anterior, remova o número 1. Mostre o estado da árvore e explique qual regra de balanceamento foi acionada.
R:                          [20]          
                    /                 \
                [5 | 10]             [35]
            /      |      \         /     \
           [2]  [6 | 8]  [15]     [30]   [40]

d. Observando a altura final da sua árvore, calcule qual seria a capacidade máxima absoluta de chaves que esta estrutura poderia armazenar antes de ser obrigada a criar um novo nível.
R:  árvore com altura 2
    raiz: 3 chaves
    intermediário: 4*3 = 12
    folhas: 4*4 = 16*3 = 48

    3 + 12 + 48 = 63 chaves