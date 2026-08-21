1. Um colega analisa um array dinâmico (que dobra de tamanho quando cheio) e afirma: "A operação de inserção é O(N), pois no pior caso temos que copiar N elementos".
Você responde: "Sim, mas o custo amortizado é O(1)". Explique com suas palavras o que vocês dois querem dizer. Quem está "certo" e em qual contexto.
 *Supondo um vetor |v| = 8, ao inserir outro elemento, seria necessário dobrar o tamanho do vetor |v| = 16, copiar os elementos antigos do vetor e inserir o novo elemento, ou seja, o pior caso de fato está contido em O(N). Porém, apenas quando o vetor estiver cheio que os elementos anteriores serão copiados para um vetor maior, portanto, o custo médio de operações é O(1)*
 *|v| = 1, 1° inserção normal (+1), 2° inserção + 2.|v| (1+1), 3° inserção + 2.|v| (2+1), 4° inserção normal (+1), 5° inserção 2.|v| (4+1), 13/5=~2,4 -> e conforme N cresce esse valor fica limitado por uma constante, O(1).*

2. Usando o Método Agregado, calcule o custo amortizado de uma inserção em um array dinâmico que, em vez de dobrar, triplica de tamanho quando fica cheio.
 *1 -> 3 -> 9 -> 27 _>...*
 **


3. Considere um contador binário de 8 bits que começa em 0. A operação é
Incrementar(). O custo real de cada incremento é o número de bits que "flipam"
(mudam de 0 para 1 ou 1 para 0).
Exemplo: Incrementar de 00000011 (3) para 00000100 (4) tem custo real 3 (dois bits
1 → 0, um bit 0 → 1). Usando o Método Agregado, qual é o custo amortizado de uma
operação Incrementar() após uma sequência de N incrementos?
4. Para o contador binário do Exercício 3, use o Método de Contabilidade.
a. Defina um "preço" (custo amortizado ĉ) para a operação Incrementar().
i. Dica: "Armazene" o crédito nos bits que são "flipados" de 0 para 1.
b. Mostre que o crédito acumulado é sempre suficiente para pagar pelos bits que
"flipam" de 1 para 0. Qual é o custo amortizado ĉ resultante?
5. Para o contador binário dos exercícios anteriores, defina uma Função de Potencial (Φ)
para provar que o custo amortizado de Incrementar() é O(1).
Dica: Uma excelente função de potencial Φ é simplesmente "o número de bits 1 no
contador".