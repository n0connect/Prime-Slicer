# Prime-Slicer

Prime-Slicer, belirli bir aralıktaki asal sayıları paralel programlama ile bulan Python programıdır.
Gerekli kütüphaneleri require_libs.py ile veya prime-slicer-libs.bat ile yükleyebilirsiniz.

![terminal-pics6](https://github.com/n0connect/Prime-Slicer/assets/126422643/f3026df6-229b-4a3f-a48d-72f603d9af40)
**5.007.654.251 ile 5.097.654.251 arasında ki 90.000.000 sayıyı 4 dakikada incelemiş ve asal olanları tespit etmiştir.**

Bu proje, belirli bir aralıktaki asal sayıları bulmak için bir algoritma kullanır. Asal sayılar, yalnızca 1 ve kendisi tarafından bölünebilen sayılardır. Proje, belirtilen bir başlangıç ve bitiş sayısı arasındaki tek sayıları seçer ve bu sayıları daha önce kaydedilmiş olan bir asal sayı listesi ile kontrol eder.

### Asal Sayı Listesi

Varsayılan olarak, projenin başlangıcında bir asal sayı listesi oluşturulur ve bu liste "saved_prime_list0.pkl" dosyasında saklanır. Bu liste, daha önceki hesaplamaların birikimi olarak elde edilir ve asal sayıları içerir. Kullanıcılar, bu kaydedilmiş listeyi kullanarak daha hızlı hesaplamalar yapabilirler.

Asal sayı listesi her başlangıçta bir dosyada saklanır. Ancak, dosyanın boyutu belirli bir sınırı aştığında (örneğin, 1MB), yeni bir asal sayı listesi oluşturulur. Örneğin, "saved_prime_list0.pkl" dosyası 1MB'ı geçerse, bir sonraki hesaplama işlemi için yeni bir liste "saved_prime_list1.pkl" adında oluşturulur.

Bu, hem bellek kullanımını optimize etmek hem de daha büyük asal sayıları saklamak için dinamik bir listeleme yöntemini sağlar.

Kullanıcılar, her program başladığında dosya boyutunu kontrol etme özelliği sayesinde, her seferinde en güncel ve uygun asal sayı listesini kullanabilirler.


### Algoritmanın İşleyişi

1. Belirtilen aralıktaki tek sayıları seç.
2. Her bir seçilen sayıyı, daha önce kaydedilmiş asal sayı listesi sayının kareköküne kadar kontrol et.
3. Eğer seçilen sayı, kareköküne kadar olan hiçbir asal sayıya tam olarak bölünmezse, o sayıyı asal olarak kabul et.
4. Asal sayıları biriktir ve sonuç listesini oluştur.

### Kümulatif Hesaplama

Bu proje, kümulatif bir şekilde asal sayıları hesaplayabilir. Her hesaplama işlemi sonrasında elde edilen asal sayılar, bir sonraki hesaplama işlemi için temel oluşturur. Kullanıcılar, son hesaplanan asal sayının karesi kadar olan bir aralıkta yeni asal sayıları hesaplamak için bu özelliği kullanabilirler.

### Kaydedilmiş Liste Kullanımı

Kullanıcılar, belirli bir aralıktaki asal sayıları daha hızlı hesaplamak için kaydedilmiş asal sayı listesini kullanabilirler. Bu, projenin daha önceki hesaplamalarını kullanarak işlem süresini optimize etmelerine olanak tanır.
Yüklediğim listelerde default kontrol listesi olan saved_prime_list0.pkl ile  84499873, Dolayısıyla 84499873² ≈ 7.14x10¹⁵ aralığında ki asal sayılar tespit edilebilir.

### Nasıl Kullanılır

Projeyi başlatırken, kullanıcılardan belirli bir aralık ve hesaplama için kullanılacak CPU, Chunk Count, Chunk Range girişleri alınır. Kullanıcılar, aynı zamanda asal sayı listesi konusunda da tercih yapabilirler.

- **CPU Girişi:** Kullanıcıdan kullanılacak CPU sayısının girişi alınır ve işlemin hızını büyük ölçüde etkiler.

- **Chunk Range:** Kullanıcının belirlediği aralıkta ki tek sayıları; Paralel olarak işçilere paylaştırmak için aralık belirler.
 ör: chunk-range=1000, a=BaşlangıçSayısı ise Kullanıcının aralığı; (a, a+1000), (a+1000, a+2000), ... olarak parçalanır.

- **Chunk Count:** Parçalanan aralığı alt gruplara böler ve her alt grubun içinde ki aralık sayısını belirler. ör: chunk-count=2 ise parçalanış şu şekildedir;
[ [ (a, a+1000), (a+1000, a+2000) ], [ (a+2000, a+3000), (a+3000, a+4000) ],  [ (a+4000, a+5000), (a+5000, a+6000) ], [ (a+6000, a+7000), (a+7000, a+8000) ]... ] ] 2 elemanlı alt gruplar oluşturur.
Bu oluşturulan alt gruplar paralel olarak aynı anda işlenmez! Aksine paralel olarak işlenenler parçalanan alt grubun içerisinde ki bütün aralıklardır; Yani Sırası ile alt gruplar işlenir, fakat paralel olarak işlenenler aralıklardır.

- **marginal-error:** Kullanıcıdan istenmez fakat config.ini dosyası üzerinden set edilebilir. karekök hesaplamalarında, hata payı olarak sayıynın kendisine eklenir.


## Çalışma Ortamı

- **Python Sürümü:** 3.12.1
- **İşletim Sistemi:** Windows 10 Home Single Language, 64-bit
- **Donanım Bilgileri:**
  - **İşlemci:** 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz   2.69 GHz
    - Çekirdek Sayısı: 6
    - Mantıksal İşlemci Sayısı: 12
  - **RAM:** 16GB


Algoritma şu adımları içerir:
1. Belirtilen aralıktaki tek sayıları seç.
2. Kaydedilmiş asal sayı listesindeki asal sayılarla böl.
3. Kareköküne kadar olan asal sayılara kadar kontrol yap ve tam bölünmezse sayı asal kabul edilir.

## Kullanılan Kütüphaneler ve Modüller

- **multiprocessing:** Paralel programlama için gerekli olan işlem havuzu ve kilitleme işlemleri sağlanmaktadır.
- **tqdm:** İşlem süresini gösteren ve kullanıcıya ilerlemeyi gösteren süreç çubukları oluşturmak için kullanılır.
- **math:** Matematiksel işlemler için kullanılır.
- **pickle:** Veri seri hale getirmek ve kaydetmek için kullanılır.
- **os:** İşletim sistemi ile ilgili işlemleri gerçekleştirmek için kullanılır.
- **sys:** Python yürütme zamanı ile ilgili sistem bilgilerine erişim sağlamak için kullanılır.
- **time:** Zaman ile ilgili işlemleri gerçekleştirmek için kullanılır.
- **configparser:** .ini dosyaları oluşturmak ve okumak için kullanılır.
- **numpy:** C ve Fortran tabanlı optimizasyon ve vektörleştirme işlemleri için kullanılır.


## Kullanım

1. Programı çalıştırın.
3. Başlangıç ve bitiş sayılarını girmeniz istenecektir. Varsayılan değerler önerilir, ancak istediğiniz aralığı seçebilirsiniz.
4. Chunk ve CPU sayısını girmeniz istenecektir. Bu, işlemin hızını etkiler. Daha fazla CPU ve chunk daha hızlı bir işlem sağlar, ancak daha fazla sistem kaynağı kullanır.
5. İşlem başladığında program aralıktaki asal sayıları hesaplar ve saved_prime_list[n].pkl ile kaydeder.

## Örnek Çıktı

Program çalıştığında, işlemin durumunu ve hesaplanan asal sayıları içeren bir çıktı alırsınız.
-> saved_prime_list7.pkl

## Proje Durumu

**Durum:** Stabil

Projenin mevcut durumu stabildir, yani temel işlevselliği sağlamaktadır ve beklenen sonuçları başarıyla üretmektedir. Ancak, projede sürekli iyileştirmeler ve ek özellikler eklemeye devam ediyorum.

![terminal-pics](https://github.com/n0connect/Prime-Slicer/assets/126422643/252dd0a5-e6bd-42db-9882-5081fbcd5539)
![terminal-pics2](https://github.com/n0connect/Prime-Slicer/assets/126422643/2aebc982-e26b-4c95-b4fa-8658b2081d9d)
![terminal-pics3](https://github.com/n0connect/Prime-Slicer/assets/126422643/3a01682a-3977-4afc-9c82-f9c208132f65)
![terminal-pics4](https://github.com/n0connect/Prime-Slicer/assets/126422643/0bad609e-e882-4c5d-b0d6-fe34bedbe916)
![terminal-pics5](https://github.com/n0connect/Prime-Slicer/assets/126422643/79261923-edae-4462-8ee0-c460aefc6982)

## İletişim

Eğer proje ile ilgili herhangi bir soru, öneri veya geri bildiriminiz varsa benimle iletişime geçebilirsiniz.

- **E-posta:** niceshotfree@gmail.com

## Lisans

Bu proje [MIT lisansı](LICENSE) altında lisanslanmıştır. Detaylı bilgi için LICENSE dosyasını inceleyebilirsiniz.
