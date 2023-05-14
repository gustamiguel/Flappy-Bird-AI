import pygame, os, random, neat, matplotlib.pyplot as plt, graphviz



# Se for falso, permite que o usuário jogue
escolha = True
while escolha:
    JOGADOR = int(input('[1 - Jogar]\n[2 - Inteligência Artificial]\n-> '))
    if JOGADOR == 1:
        IA_jogando = False
        escolha = False
    elif JOGADOR == 2:
        IA_jogando = True
        escolha = False
    else:
        print('Digite 1 ou 2!') 

        
geracao = 0


TELA_LARGURA = 500
TELA_ALTURA = 800

IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]
IMAGEM_GERACAO = pygame.transform.scale(pygame.image.load(os.path.join('imgs', 'gen.png')), (42, 42))

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)

class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y
        
    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo
        # restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2
            
        self.y += deslocamento    
        
        # angulo do pássaro
        
        if deslocamento < 0 or self.y < (self.altura + 10):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO
    def desenhar(self, tela):
        # definir qual imagem do passaro usar
        self.contagem_imagem += 1
        
        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem <= self.TEMPO_ANIMACAO*4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0
        # se o passaro tiver caindo, não bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO*2
        # desenhar a imagem
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)
        
    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)
        
        
class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5
    
    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()
        
    def definir_altura(self):
        self.altura = random.randint(50, 450)
        self.pos_topo =  self.altura - self.CANO_TOPO.get_height()
        # Defini que quando a IA jogar terá uma randomização da distância entre o cano de cima e o cano de baixo.
        if IA_jogando:
            self.pos_base =  self.altura + random.randrange(158, 200, 2)
        if not IA_jogando:
            self.pos_base = self.altura + self.DISTANCIA
    def mover_cano(self):
        self.x -= self.VELOCIDADE
        
    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))
        
    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)
        
        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))
        
        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)
        
        if base_ponto or topo_ponto:
            return True
        else:
            return False
class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA
        
    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA
            
    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))
        
def desenhar_tela(tela, passaros, canos, chao, pontos):  
    tela.blit(IMAGEM_BACKGROUND, (0, 0)) 
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)    
    texto = FONTE_PONTOS.render(f'{pontos}', 1, (255,255,255))
    tela.blit(texto, (TELA_LARGURA - texto.get_width(), 5))
    
    
    # Se a IA estiver jogando, desenha na tela
    if IA_jogando:
        tela.blit(IMAGEM_GERACAO, (2, 5))
        texto = FONTE_PONTOS.render(f'{geracao}', 1, (255,255,255))
        tela.blit(texto, (50, 5))
    
    chao.desenhar(tela)
    pygame.display.update()

def main(genomas, config): # Fitness function (Para funcionar precisa de dois parâmetros, neste caso 'genomas' e 'config')
    global geracao
    geracao += 1
    
    if IA_jogando:
        redes = []
        lista_genomas = []
        passaros = []
        for _, genoma in genomas:
            rede = neat.nn.FeedForwardNetwork.create(genoma, config)
            redes.append(rede)
            genoma.fitness = 0
            lista_genomas.append(genoma)
            passaros.append(Passaro(230, 350))
    else:
        passaros = [Passaro(230, 350)]
    chao = Chao(730)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()
    
    rodando = True
    while rodando:
        relogio.tick(30)
        # Interações Usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                quit()
            if not IA_jogando:
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()
                            
        indice_cano = 0
        if len(passaros) > 0:
            if len(canos) > 1 and passaros[0].x > (canos[0].x + canos[0].CANO_TOPO.get_width()): # Qual cano olhar
                indice_cano = 1
        else:
            rodando = False
            if not IA_jogando:
                print("Você perdeu, tente novamente.")
            break
        
        # Mover Coisas
        for i, passaro in enumerate(passaros):
            passaro.mover()
            # aumentar um pouco a fitness do pássaro
            if IA_jogando:
                lista_genomas[i].fitness += 0.1
                output = redes[i].activate((passaro.y, 
                                            abs(passaro.y - canos[indice_cano].altura), 
                                            abs(passaro.y - canos[indice_cano].pos_base)))
                # -1 e 1 -> se o output for > 0.5 então o pássaro pula
                if output[0] > 0.5:
                    passaro.pular()
        chao.mover()
        
        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if IA_jogando:
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)
                        redes.pop(i)
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
                    
            cano.mover_cano()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)
        
        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))
            if IA_jogando:
                for genoma in lista_genomas:
                    genoma.fitness += 5
                
        for cano in remover_canos:
            canos.remove(cano)
        
        for i, passaro in enumerate(passaros):
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if IA_jogando:
                    lista_genomas[i].fitness -= 1
                    lista_genomas.pop(i)
                    redes.pop(i)
        
        desenhar_tela(tela, passaros, canos, chao, pontos)
        
def rodar(caminho_config):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                caminho_config)
    
    populacao = neat.Population(config)
    populacao.add_reporter(neat.StdOutReporter(True))
    populacao.add_reporter(neat.StatisticsReporter())
    
    if IA_jogando:
        populacao.run(main, 50)       
    else:
        main(None, None)
        
        
if __name__ == '__main__':
    caminho_config = 'config.txt'
    rodar(caminho_config)