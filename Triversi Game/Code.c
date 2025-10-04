#include <stdio.h>

int main() {
	
	int N,i,j,x,y,v,w,m,n,p,q;
	int orta1, orta2, ctrl=0, renk_degisim=0;
	int sayac, kirmizisayac=0, sarisayac=0, mavisayac=0;
	char A[23][23], renk;
	
	printf("1. Oyuncu -> Kirmizi (K)\n2. Oyuncu -> Sari (S)\n3. Oyuncu -> Mavi (M)\n\n");
	printf("Triversi oyunu icin kare tahtanin satir/sutun sayisini giriniz: ");
	scanf("%d", &N);
	
	while (N<3 || N>23){
		printf("Kare tahtanin boyutu 3-23 arasinda olmalidir. Tekrar kare tahtanin satir sayisini giriniz: ");
		scanf("%d",&N);
	}
	
	printf("\nBaslangic Kare Tahtasi: \n");
	for (i=0;i<N;i++){
		for(j=0;j<N;j++){
			A[i][j]='-';
			printf("%c ",A[i][j]);
		}
		printf("\n");
	}
	printf("\n");
	
	i=0;
	printf("%d. Oyuncu (K) rengi icin hamlenizi yapiniz: \nx ve y koordinatlari tahtanin ortasinda olacak sekilde giriniz: ",(i%3)+1);
	scanf("%d %d",&x,&y);
	if (N%2!=0){
		orta1=(N/2)+1;
		orta2=orta1;
	}
	else{
		orta1=(N/2);
		orta2=(N/2)+1;
	}
	
	while (x<orta1 || x>orta2 || y<orta1 || y>orta2){
		printf("x ve/veya y degerleri hatali tekrar giriniz: ");
		scanf("%d %d",&x, &y);
	}  
	
	A[x-1][y-1]='K';
	
	printf("\nOlusan matris:\n");
	for (p=0;p<N;p++){
		for (q=0;q<N;q++){
			printf("%c ",A[p][q]);
		}
		printf("\n");
	}
	printf("\n");
	i++;
	
	sayac=N*N;
	
	while (i<sayac){
		renk_degisim=0;

		if (i%3==0) renk = 'K'; 
		else if (i%3==1) renk = 'S';
		else if (i%3==2) renk = 'M';
		
		printf("%d. Oyuncu (%c) rengi icin hamlenizi yapiniz: \nx ve y koordinatlari giriniz: ",(i%3)+1,renk);
		scanf("%d %d",&x,&y);
		
		v=x-1;
		w=y-1;
		while (x <= 0 || x > N || y <= 0 || y > N || A[v][w] != '-' ||
			((v - 1 < 0 || w - 1 < 0 || A[v - 1][w - 1] == '-') &&
            (v - 1 < 0 || A[v - 1][w] == '-') &&
            (v - 1 < 0 || w + 1 >= N || A[v - 1][w + 1] == '-') &&
            (w - 1 < 0 || A[v][w - 1] == '-') &&
            (w + 1 >= N || A[v][w + 1] == '-') &&
            (v + 1 >= N || w - 1 < 0 || A[v + 1][w - 1] == '-') &&
            (v + 1 >= N || A[v + 1][w] == '-') &&
            (v + 1 >= N || w + 1 >= N || A[v + 1][w + 1] == '-'))) {
			printf("x ve/veya y degerleri hatali tekrar giriniz: ");
			scanf("%d %d",&x, &y);
			v=x-1;
			w=y-1;
		}
				
		A[v][w]=renk;
		
		printf("\nOlusan matris:\n");
		for (m=0;m<N;m++){
			for (n=0;n<N;n++){
				printf("%c ",A[m][n]);
			}
			printf("\n");
		}
		printf("\n");
		
		m=v;
		n=w-2;
		if (A[m][n+1]!='-' && A[m][n+1]!=renk){
			while (n>=0 && ctrl==0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					for (p=n;p<w;p++){
						A[m][p] = renk;
					}
					ctrl=1;
					renk_degisim=1;
				}	
				n--;
			}
		}
		ctrl=0;
		
		m=v;
		n=w+2;
		if (A[m][n-1]!='-' && A[m][n-1]!=renk){
			while (n<N && ctrl == 0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					for (p=n;p>w;p--){
						A[m][p] = renk;
					}
					ctrl=1;
					renk_degisim=1;
				}
				n++;
			}
		}
		ctrl=0;
		
		m=v-2;
		n=w;
		if (A[m+1][n]!='-' && A[m+1][n]!=renk){
			while (m>=0 && ctrl==0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					for (p=m;p<v;p++){
						A[p][n]=renk;
					}
					ctrl=1;
					renk_degisim=1;
				}				
				m--;
			}
		}
		ctrl=0;
		
		m=v+2;
		n=w;
		if (A[m-1][n]!='-' && A[m-1][n]!=renk){
			while (m<N && ctrl==0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					for (p=m;p>v;p--){
						A[p][n]=renk;
					}
					ctrl=1;
					renk_degisim=1;
				}	
				m++;
			}
		}
		ctrl=0;
		
		m=v-2;
		n=w+2;
		if (A[m+1][n-1]!='-' && A[m+1][n-1]!=renk){
			while (m>=0 && n<N && ctrl==0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					p=m;
					q=n;
					while (p<v && q>w){
						A[p][q]=renk;
						p++;
						q--;
					}
					ctrl=1;
					renk_degisim=1;	
				}
				m--;
				n++;
			}
		}
		ctrl=0;
		
		m=v+2;
		n=w-2;
		if (A[m-1][n+1]!='-' && A[m-1][n+1]!=renk){
			while (m<N && n>=0 && ctrl==0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					p=m;
					q=n;
					while (p>v && q<w){
						A[p][q]=renk;
						p--;
						q++;
					}
					ctrl=1;
					renk_degisim=1;	
				}
				m++;
				n--;
			}
		}
		ctrl=0;
		
		m=v-2;
		n=w-2;
		if (A[m+1][n+1]!='-' && A[m+1][n+1]!=renk){
			while (m>=0 && n>=0 && ctrl==0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					p=m;
					q=n;
					while (p<v && q<w){
						A[p][q]=renk;
						p++;
						q++;
					}
					ctrl=1;
					renk_degisim=1;
				}
				m--;
				n--;
			}
		}
		ctrl=0;
		
		m=v+2;
		n=w+2;
		if (A[m-1][n-1]!='-' && A[m-1][n-1]!=renk){
			while (m<N && n<N && ctrl==0 && A[m][n]!='-'){
				if (A[m][n]==renk){
					p=m;
					q=n;
					while (p>v && q>w){
						A[p][q]=renk;
						p--;
						q--;
					}
					ctrl=1;
					renk_degisim=1;	
				}
				m++;
				n++;
			}
		}
		ctrl=0;
		
		if (renk_degisim==1){
			printf("RENK DEGISIMI:\n");
						for (p=0;p<N;p++){
							for (q=0;q<N;q++){
								printf("%c ",A[p][q]);	
							}
							printf("\n");
						}
						printf("\n");	
		}
			
		
		
		i++;
	}

	for (i=0;i<N;i++){
		for (j=0;j<N;j++){
			if (A[i][j]=='K') kirmizisayac++;
			else if (A[i][j]=='S') sarisayac++;
			else if (A[i][j]='M') mavisayac++;
		}
	}
	
	printf("Kirmizi Taslar Sayisi: %d\nSari Taslar Sayisi: %d\nMavi Taslar Sayisi: %d\n\n",kirmizisayac,sarisayac,mavisayac);
	
	if (kirmizisayac > sarisayac && kirmizisayac>mavisayac)
		printf("1. OYUNCU KAZANDI");
	else if (sarisayac>kirmizisayac && sarisayac >mavisayac)
		printf("2. OYUNCU KAZANDI");
	else if (mavisayac> kirmizisayac && mavisayac>sarisayac)
		printf("3. OYUNCU KAZANDI");
	else printf("BERABERLIK");
	
	return 0;
}
