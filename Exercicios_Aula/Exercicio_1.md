2. Considere a implementação de uma fila utilizando duas pilhas (uma para inserções e outra para remoções). Demonstre que, mesmo que ocasionalmente uma transferência inteira de elementos seja necessária, o custo amortizado de cada operação (enqueue/dequeue) é (O(1)).
*RESPOSTA: ex: P1: [1,2,3] P2: []  -> dequeue  P1: [] P2:[3,2,1]*
*Em N elementos em P1, são N operações de push/pop para P2, custando O(n). 1+1+1 = 3 (enqueue em P1), 1+1+1+1= 4 (dequeue para P2 mais a retirada do ultimo elemento), entretanto, os demais dequeue não precisam de transferência, portanto 3+4+2/6=1,5*
*Ou seja, apesar de um dequeue ter custo alto, a média ficou constante.*

3. Vimos que dobrar o tamanho do array garante um custo amortizado de O(1). Imagine agora que um desenvolvedor inexperiente decidiu que dobrar gasta muita memória. Em vez disso, ele implementou um array que, ao encher, aumenta seu tamanho adicionando sempre um número constante k de novos espaços (por exemplo, aumenta de 10 em 10 espaços). O custo de redimensionar continua sendo copiar os elementos antigos.
a. Assuma que k = 1 (o array cresce apenas 1 espaço por vez ao encher)Calcule o custo real de cada uma das n inserções (do elemento 1 até o elemento n).
*RESPOSTA: custo de cada inserção: elementos copiados + novo elemento, ou seja, na n-ésima inserção, o custo será de n. O Custo total de inserções é de (n(n+1))/2 = T(n), logo, T(n) = O(n^2)*
*Portanto o custo amortizado é de = O(n)*
*ex: 1° inserção 0+1=1; 2° inserção 1+1=2; 3° inserção 2+1=3; ...*
b. Por que arrays dinâmicos modernos usam fator multiplicativo e não aditivo? Responda através da demonstração matemática do aumento de custo dessa abordagem com relação à política de dobrar o tamanho do array.
*RESPOSTA: Por meio do crescimento aditivo, ao aumentar de 1 em 1: 1 + 2 + 3 + ... + n = O(n^2) elementos, portanto o custo amortizado é O(n). Já com o crescimento multiplicativo, ao dobrar: 1 + 2 + 4 + 8 + ... + n = O(n), logo o custo amortizado é O(1)*
*O cresimento multiplicativo é mais eficiente porque reduz o custo amortizado de O(n) para O(1).*