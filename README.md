# Prime-Slicer

Prime-Slicer, belirli bir aralıktaki asal sayıları paralel programlama ile bulan Python programıdır.

## Çalışma Ortamı

- **Python Sürümü:** 3.12.1
- **İşletim Sistemi:** Windows 10 Home Single Language, 64-bit
- **Donanım Bilgileri:**
  - **İşlemci:** 11th Gen Intel(R) Core(TM) i5-11400H @ 2.70GHz   2.69 GHz
    - Çekirdek Sayısı: 6
    - Mantıksal İşlemci Sayısı: 12
  - **RAM:** 16GB

## Kullanılan Kütüphaneler ve Modüller

- **multiprocessing:** Paralel programlama için gerekli olan işlem havuzu ve kilitleme işlemleri sağlanmaktadır.
- **tqdm:** İşlem süresini gösteren ve kullanıcıya ilerlemeyi gösteren süreç çubukları oluşturmak için kullanılır.
- **math:** Matematiksel işlemler için kullanılır.
- **pickle:** Veri seri hale getirmek ve kaydetmek için kullanılır.
- **os:** İşletim sistemi ile ilgili işlemleri gerçekleştirmek için kullanılır.
- **sys:** Python yürütme zamanı ile ilgili sistem bilgilerine erişim sağlamak için kullanılır.
- **time:** Zaman ile ilgili işlemleri gerçekleştirmek için kullanılır.
- **gc:** Manuel bellek temizleme işlemleri için kullanılır.
- **configparser:** .ini dosyaları oluşturmak ve okumak için kullanılır.


## Kullanım

1. Programı çalıştırın.
3. Başlangıç ve bitiş sayılarını girmeniz istenecektir. Varsayılan değerler önerilir, ancak istediğiniz aralığı seçebilirsiniz.
4. Chunk ve CPU sayısını girmeniz istenecektir. Bu, işlemin hızını etkiler. Daha fazla CPU ve chunk daha hızlı bir işlem sağlar, ancak daha fazla sistem kaynağı kullanır.
5. İşlem başladığında program aralıktaki asal sayıları hesaplar ve saved_prime_list[n].pkl ile kaydeder.

## Örnek Çıktı

Program çalıştığında, işlemin durumunu ve hesaplanan asal sayıları içeren bir çıktı alırsınız.
-> saved_prime_list0.pkl

## Proje Durumu
STABIL

## Lisans

Bu proje [MIT lisansı](LICENSE) altında lisanslanmıştır. Detaylı bilgi için LICENSE dosyasını inceleyebilirsiniz.
