from multiprocessing import Lock, Pool, Manager  # Paralel programlama için Lock, ve İşlem havuzu Pool
import multiprocessing  # Paralel programlama
from tqdm import tqdm  # ProcessBar
import configparser  # .ini Dosyası oluşturmak için
import math
import pickle
import os
import sys
import time

# GLOBAL VARIABLES
user_end_number_: int  # Kullanıdan alınan bitiş değerini bellekte tutar.
start_number_: int  # Kullanıdan alınan bailangıç değerini bellekte tutar.
last_digit_ = 0  # Son kaydedilen .pkl dosyasının sayı değerini bellekte tutar.
temp_num_ = 0  # Yüklenilen .pkl dosyasının sayı değerini bellekte tutar.
loaded_list: list  # Kontrol için yüklenen .pkl dosyası bu listede tutulur.
new_created_file_name_: str  # Yeni oluşan yada son kaydedilen .pkl dosyasının ismi.
loaded_prime_list_name: str  # Asal sayı kontrolünü yapacak liste belirlenir.
user_min_value_: int  # Kullanıcının girebileceği min başlangıç değeri.
marginal_error: int = 10  # Karekök ve Algoritmik hatalardan kaçınmak için (default=10)

lock = Lock()  # Paralel çalışan parçacıklar için kilit mekanizması


def start_program():
    file_size_control()
    take_user_number()
    update_ini_()
    read_ini_()
    approx_calculation_of_probability()
    load_with_this_value_prime_list()


def update_ini_():
    # Eğer .ini yoksa oluşturur
    global start_number_
    global user_end_number_
    global user_min_value_
    global last_digit_
    global new_created_file_name_
    global loaded_prime_list_name
    global marginal_error

    # Config nesnesi oluşturulur
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    # .ini dosyasının varlığını kontrol eder
    ini_is_alive = os.path.exists(config_file)

    # .ini Dosyasına kaydedilebilir formata getirmek
    _start_number_ = str(start_number_)
    _user_end_number_ = str(user_end_number_)
    _user_min_value_ = str(user_min_value_)
    _last_digit_ = str(last_digit_)
    _new_created_file_name_ = str(new_created_file_name_)

    # .ini yok ise oluştur
    if not ini_is_alive:
        config.add_section('Settings')
        config.add_section('Recommended Settings')

        # Değişen değerleri oluştur
        config.set('Recommended Settings', 'marginal-error', '10')
        config.set('Settings', 'current-loading-pkl-name', 'saved_prime_list0.pkl')

    config.read(config_file)  # .ini dosyasını oku

    # Değiştirilebilir değerler .ini içerisinden ayarlanabilir değerler
    _loaded_prime_list_name = config.get('Settings', 'current-loading-pkl-name')
    _marginal_error = config.get('Recommended Settings', 'marginal-error')

    # Değişen değerler
    config.set('Settings', 'start-number', _start_number_)
    config.set('Settings', 'end-number', _user_end_number_)
    config.set('Settings', 'last-calculated-num', _user_min_value_)
    config.set('Settings', 'count-of-pkl', _last_digit_)
    config.set('Settings', 'current-saving-pkl-name', _new_created_file_name_)
    config.set('Settings', 'current-loading-pkl-name', _loaded_prime_list_name)

    # Önerilen değerler
    config.set('Recommended Settings', 'cpu-count', '4')
    config.set('Recommended Settings', 'chunk-count', '4')
    config.set('Recommended Settings', 'marginal-error', _marginal_error)

    try:
        # .ini dosyasını oluşturun
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    except configparser.ParsingError as ex:
        print(f"Error parsing .ini file: {ex}")
    except Exception as es:
        print(f"Error updating .ini file: {es}")


def read_ini_():
    # .ini dosyasını oku
    global start_number_
    global user_end_number_
    global user_min_value_
    global last_digit_
    global new_created_file_name_
    global loaded_prime_list_name
    global marginal_error

    config = configparser.ConfigParser()

    # .ini dosyasını okur
    config.read('config.ini')

    _start_number_ = config.get('Settings', 'start-number')
    _user_end_number_ = config.get('Settings', 'end-number')
    _user_min_value_ = config.get('Settings', 'last-calculated-num')
    _last_digit_ = config.get('Settings', 'count-of-pkl')
    _new_created_file_name = config.get('Settings', 'current-saving-pkl-name')
    _loaded_list_ = config.get('Settings', 'current-loading-pkl-name')
    _marginal_error = config.get('Recommended Settings', 'marginal-error')

    # Değerler ile eşleştir
    start_number_ = int(_start_number_)
    user_end_number_ = int(_user_end_number_)
    user_min_value_ = int(_user_min_value_)
    last_digit_ = int(_last_digit_)
    new_created_file_name_ = _new_created_file_name

    # Değiştirilebilir değerleri yükle.
    loaded_prime_list_name = _loaded_list_
    marginal_error = int(_marginal_error)


def file_size_control():
    # Program ilk çalıştığında kaydedilen .pkl dosyalarını kontrol eder
    global new_created_file_name_
    global last_digit_

    try:
        print(f"_" * 60)  # FOR GOOD SEEN
        saved_files_list = os.listdir(os.getcwd())  # Dizinde ki dosyaları al
        for file in saved_files_list:
            if file.endswith('.pkl'):  # .pkl olanları seç
                last_saved_file = file  # Kaydedilen .pkl son elemanı
                print(f"Saved Prime list {file}: {os.stat(file).st_size / (1024 ** 2)} MB")  # Boyut Kontrolü
                print(f"_" * 60)  # Sadece görsellik için

        if 1 <= os.stat(last_saved_file).st_size / (1024 ** 2):  # Boyutu 1MB fazla ise
            print(f"{last_saved_file:>30} size is max.")
            print(f"_" * 60)
            last_digit_ = remove_character_in_file_name(last_saved_file)  # Son kaydedilen sayıyı al ör:5
            new_created_file_name_ = f'saved_prime_list{last_digit_ + 1}.pkl'  # Yeni .pkl dosyası 6 olur
            create_new_pkl_file_()  # yeni .pkl oluştur
        else:
            last_digit_ = remove_character_in_file_name(last_saved_file)  # Son .pkl sayısını al ör:5
            new_created_file_name_ = f'{last_saved_file}'  # Son .pkl ile işleme devam edilir ör:5

            # Dosyalar Hakkında Bilgi Yazdırmak
        information_about_saved_pkl_()

    except Exception as ex:
        raise print(f"{ex}")


def remove_character_in_file_name(last_saved_file):
    # Kaç tane .pkl dosyasının kayıtlı olduğu sayısıdır.
    digits = ''.join(filter(str.isdigit, last_saved_file))
    if digits:
        digits = int(digits)
    else:
        digits = 0
    return digits


def create_new_pkl_file_():
    # 1MB aşan dosya varsa bu fonksiyon yeni bir .pkl oluşturur.
    global last_digit_

    try:
        with open(f'saved_prime_list{last_digit_ + 1}.pkl', 'wb') as new_pkl_:
            new_pkl_.close()
    except Exception as ex:
        print(f"saved_prime_list{last_digit_ + 1}.pkl is not created: {ex}")


def take_user_number():
    global user_end_number_, start_number_

    print("""
    This program has been developed with a new algorithm to find prime numbers faster,
    the basic principle of this algorithm is to use the prime numbers that exist up to
    a certain range to determine the status of other numbers.

    If you have used the program before ignore the default values, you also need to start
    by giving the starting number and the final number a number larger than the last number
    in the list you calculated.

        \033[1mThis program can be dangerous for your computer if you don't know exactly what you are doing,
        use the recommended Chunk and Cpu values\033[0m

    """)
    while True:
        try:
            start_number_ = int(input(f"Enter a ODD positive start number(default: number>={user_min_value_}): "))
            user_end_number_ = int(input(f"Enter a ODD last number: "))
            start_number_ = min(start_number_, user_min_value_)  # Kullanıcı dostu bir seçim
            if start_number_ <= 0 or user_end_number_ <= 0 or start_number_ >= user_end_number_:
                raise ValueError
            if start_number_ % 2 == 0 or user_end_number_ % 2 == 0:
                raise print("Please Enter two ODD number.")
            if start_number_ < user_min_value_:
                raise print(f"You have already worked in this range enter the end number; >{user_min_value_}")
            if user_end_number_ <= user_min_value_:
                user_end_number_ = user_min_value_ + 100
                print(f"Default choice for the last number: {user_min_value_ + 100}")
            break  # Eğer istenilen sayılar girilirse fonksiyonu bitir.
        except ValueError as er:
            print(f"{er}")
        except Exception as ex:
            print(f"{ex}")


def approx_calculation_of_probability() -> None:
    # Yaklaşık Asal Miktarı ve Yoğunluğunu hesaplar
    global user_end_number_
    global start_number_

    average_prime_ = (user_end_number_ / math.log(user_end_number_)) - (start_number_ / math.log(start_number_))
    density_of_primes_ = 100 * (average_prime_ / (user_end_number_ - start_number_))
    print(f"_" * 60)
    print(f"\033[1mAverage prime number count between ≈ {int(average_prime_)}\033[1n")
    print(f"\033[1mDensity of prime between than ≈ %{int(density_of_primes_)}\033[1n")
    print(f"_" * 60)
    time.sleep(5)  # İncelenmek için 5sn bekler


def load_with_this_value_prime_list():
    global last_digit_
    global loaded_list
    global temp_num_
    global loaded_prime_list_name

    try:
        with open(f'{loaded_prime_list_name}', 'rb') as saved_file:
            loaded_list = pickle.load(saved_file)
            return ":)"
    except Exception as ex:
        print(f"\n{loaded_prime_list_name} file is broken: {ex}")
        print("Please Delete Broken and Empty Files. And Restart The Program")


def information_about_saved_pkl_():
    global new_created_file_name_
    global last_digit_
    global user_min_value_

    total_primes_ = 0  # Toplam hesaplanan Asal Sayı adedi

    for temp_num in range(0, last_digit_ + 1, 1):
        try:
            with open(f'saved_prime_list{temp_num}.pkl', 'rb') as dump_in_terminal:
                dump_list = pickle.load(dump_in_terminal)
                if not dump_list:
                    raise print("\033[1m_EmptyFile_\033[1n")
                len_of_list = len(dump_list)
                user_min_value_ = dump_list[-1]
                total_primes_ += len_of_list
                print(f'saved_prime_list{temp_num}.pkl;')
                print(f"The prime number at the top of the list: {dump_list[0]}")
                print(f"The prime number at the end of the list: {dump_list[-1]}")
                print(f"the list contains {len_of_list} prime numbers")
                print(f"_" * 60)
        except Exception as ex:
            print(f"saved_prime_list{temp_num}.pkl file is broken: {ex}")
            print("Please Delete Broken and Empty Files. And Restart The Program")
            print(f"_" * 60)
    print(f"\033[1mTotal number of calculated primes in the saved .pkl files: {total_primes_}\033[1n")


def crop_the_list(list_: list) -> list:
    global user_end_number_
    global marginal_error

    sqrt_end = math.sqrt(user_end_number_) + marginal_error + 100

    # Özel bir hata mesajı
    if not sqrt_end <= list_[-1]:
        print(f"""\033[1m
        Since the square root of {sqrt_end}, the last number you selected,
        is greater than the last element of 'saved_prime_list0.pkl', the list
        that tests for prime numbers, the process is terminated.

        Solution: Load a larger prime checklist or merge two prime lists :)\033[1n
        """)
        sys.exit(1)

    # Orijinal listeyi değiştirmek yerine yeni bir liste oluştur
    cropped_list = [item for item in list_ if item <= sqrt_end]

    return cropped_list


def save_prime_list(list_):
    global new_created_file_name_

    if not list_:
        print("List is empty. No need to save.")
        return

    # Liste içinde listeler yapısını düzleştir.
    flat_results = [item for sublist in list_ for item in sublist
                    if item is not None and item <= user_end_number_]

    # Özel bir durumdur.
    if len(flat_results) == 1:
        print("\033[1m No Prime Between Your Selected Range\033[1n")
        kill_the_program()

    # aSencron kaydedilen Asal sayılar sıralanır.
    flat_results = sorted(flat_results)

    try:
        with open(f'{new_created_file_name_}', 'wb') as temp_list:
            pickle.dump(flat_results, temp_list)

    except Exception as ex:
        print(f"Saving Error: {ex}")


def is_prime(number, primes):
    #sqrt_of_num = None

    sqrt_of_num = math.isqrt(number)

    for prime in primes:
        if sqrt_of_num <= prime:
            return True
        if number % prime == 0:
            return False

    print(f"Exeption number {number}, {sqrt_of_num}, {primes[-1]} [PROGRAM CAN NOT DEFİNE IS PRIME OR NOT]")
    sys.exit(1)  # Bug Bölgesi [CriticArea]


def worker(chunk, shared_primes):
    try:
        start, end = chunk  # Gönerilen aralık oluşturulur ve paralel işlenir
        local_results = []  # Her işçinin kendi kayıt listesi

        for number in range(start, end + 1, 2):
            if is_prime(number, shared_primes):
                local_results.append(number)
    except Exception as e:
        # Multiprocessing hatası durumunda programı sonlandır
        print(f"An error occurred in multiprocessing: {e}")
        raise SystemExit

    return local_results


def choose_cpu_count():
    mp_count = multiprocessing.cpu_count()

    print(f"_" * 60)
    print(f"""
    If you're unsure about the optimal choice, consider the following:

    More CPU can lead to Faster processing but might require additional system resources.

    \033[1mTotal CPU count: {mp_count}
    Recommended range: [{mp_count // 2}, {mp_count}]\033[0m

    Choose a value based on your system's capabilities:
    \033[1m- If you have a powerful system, you can experiment with higher values for faster processing.
    - For resource-conscious use, stick to the recommended range or lower.\033[0m

    Keep in mind that the ideal value may vary based on your \033[1m"specific hardware"\033[0m and workload.
    """)
    print(f"_" * 60)

    try:
        mp_count = multiprocessing.cpu_count()

        while True:
            cpu_count_ = int(input("Enter the number of CPUs to use for the process: "))
            cpu_count_ = max(cpu_count_, mp_count // 2)  # min cpu kullanıcıya göre seç
            if cpu_count_ < mp_count // 2 or cpu_count_ > mp_count:
                raise ValueError(f"Invalid choice! Please enter a value between {mp_count // 2} and {mp_count}.")
            print(f"_" * 60)
            print(f"\033[1mWe are going to use {cpu_count_} CPUs for the process.\033[0m")
            time.sleep(2)  # incelemek için
            return cpu_count_

    except ValueError as ve:
        print(f"Error: {ve}")
        print("Please enter a valid integer between the recommended range.")
        return choose_cpu_count()

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        print("Please try again.")
        return choose_cpu_count()


def chose_num_of_chunks():
    print("""
    If you're unsure about the optimal choice, consider the following:

    More CHUNKS can lead to Faster processing but might require additional system resources.
    Fewer CHUNKS might be slower but can be more resource-efficient.
    
    \033[1mTotal CPU count: {mp_count}\033[0m
    
    Recommended Value Range: \033[1m[4, 8]\033[0m
    Max Value Range: \033[1m12\033[0m

    \033[1mChoose a value based on your system's capabilities:
    - If you have a powerful system, you can experiment with higher values for faster processing.
    - For resource-conscious use, stick to the recommended range or lower.\033[0m

    Keep in mind that the ideal value may vary based on your specific hardware and workload.
    """)
    print(f"_" * 60)
    try:
        mp_count = multiprocessing.cpu_count()

        while True:
            chunk_count = int(input("\033[1mEnter the number of chunks to divide the task into: \033[0m"))
            chunk_count = max(chunk_count, 4)  # Kullanıcının seçimini min 4 olarak seç
            if chunk_count > mp_count or chunk_count <= 0 or chunk_count > 12:
                raise ValueError(f"Invalid choice! Please enter a value between {mp_count // 2} and 8.")

            print(f"\033[1mWe are going to use {chunk_count} chunks to distribute the task.\033[0m")
            print(f"_" * 60)
            time.sleep(2)   # İncelemek için.
            return chunk_count

    except ValueError as ve:
        print(f"Error: {ve}")
        print("Please enter a valid integer between the recommended range.")
        return chose_num_of_chunks()

    except KeyboardInterrupt:
        sys.exit(0)

    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        print("Please try again.")
        return chose_num_of_chunks()


def chunks_grouped(slice_count):
    # Artık sadece tek sayı olanlar tutulacak şekilde düzenlendi
    global start_number_, user_end_number_

    # Listeyi oluştur
    chunk_list = [(i, i + 1000) for i in range(start_number_, user_end_number_ + 2, 1000)]

    # Liste parçalanmalarını belirle
    chunk_size = len(chunk_list) // slice_count

    # chunks elemanlarını her biri slice_count adet gruplar halinde alt listelere böl
    chunks = [chunk_list[i * slice_count:(i + 1) * slice_count] for i in range(chunk_size + 1) if
              len(chunk_list[i * slice_count:(i + 1) * slice_count]) > 0 or i * slice_count >= chunk_size]

    return [tuple(chunk) for chunk in chunks]  # Listeyi dön


def len_of_the_chunk() -> int:
    global start_number_, user_end_number_

    len_of_chunk: int = 0

    for _ in range(start_number_, user_end_number_ + 2, 1000):
        len_of_chunk += 1

    return len_of_chunk


def main() -> None:
    global loaded_list, start_number_

    num_processes = choose_cpu_count()  # Kullanılacak cpu sayısını seç
    num_of_chunks = chose_num_of_chunks()  # Aynı anda işlenecek chunk sayısı (Balanced)
    cropped_list_ = crop_the_list(loaded_list)  # Yüklü Asal Sayı Listesini Kırpmak
    start_time = time.time()  # Süreyi başlat.
    len_of_chunks: int = len_of_the_chunk()  # Parçalanacak aralığın uzunluğunu bul

    # Paralel işlemeye başla.
    with Pool(processes=num_processes) as pool:
        chunk_results = []
        pbar = tqdm(total=len_of_chunks, desc="Processing Chunks", position=0, leave=True)  # progress bar oluştur

        # Parçalanmış chunks listesini alt(num_of_chunks) parçalara böl
        for chunk_group in chunks_grouped(num_of_chunks):

            try:    # chunk_group tuplesi paralel aSencron işlenir
                results_list = [
                    pool.apply_async(worker, args=(chunk, cropped_list_), callback=lambda _: pbar.update(1))
                    for chunk in chunk_group
                ]

                # Sonuçları toplamak için bekleyin
                chunk_results += [result.get() for result in results_list]

            except Exception as e:
                # Multiprocessing hatası durumunda programı sonlandır
                print(f"An error occurred in multiprocessing: {e}")
                raise SystemExit
            except KeyboardInterrupt:
                sys.exit(0)  # CTRL + C SONLANDIR

    # Toplam çalışma süresi
    finish_time = time.time()
    print(f"\033[1mTotal Calc. Time: {finish_time - start_time} second(s) / "
          f"{(finish_time - start_time) / 60} minute\033[1n")

    save_prime_list(chunk_results)  # Son defa kaydet

    information_about_saved_pkl_()  # Bilgi ver.
    kill_the_program()  # Programı sonlandır


def kill_the_program():
    # Diğer işlemler
    print("Processing completed successfully.")
    print("\033[1m:) boom\033[1n")
    sys.exit(1)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    start_program()
    main()

"""
Bu kod, verilen başlangıç (start_number) ve bitiş (end_number) sayıları arasındaki asal sayıları bulan bir 
programdır. Kodun adım adım nasıl çalıştığını anlamak için şu adımları takip edebiliriz:

main fonksiyonu kullanıcıdan başlangıç ve bitiş sayılarını alır. primes ve results adında iki liste tanımlanır. 
primes liste, asal sayıları depolamak için kullanılır. results liste ise worker fonksiyonu tarafından hesaplanan asal 
sayıları depolamak için kullanılır. chunks adında bir liste oluşturulur. Bu liste, iş parçacıkları (chunks) arasında 
paylaşılan aralığı temsil eder. multiprocessing.Manager() ile bir yönetici oluşturulur ve primes ve results listeleri 
bu yönetici ile yönetilir. is_prime fonksiyonu, bir sayının asal olup olmadığını kontrol eder. Bu fonksiyon, 
daha önce hesaplanan asal sayılar listesini kullanarak kontrolü gerçekleştirir. worker fonksiyonu, belirli bir 
aralıktaki (chunk) asal sayıları hesaplar ve sonuçları results listesine ekler. main fonksiyonu, başlangıçtan bitişe 
kadar olan sayılar arasındaki asal sayıları hesaplamak için iş parçacıkları kullanır. İş parçacıkları, belirli bir 
aralıktaki asal sayıları hesaplamak için worker fonksiyonunu kullanır. Program sona erdiğinde, hesaplanan asal 
sayılar final_results listesine eklenir, sıralanır ve ekrana yazdırılır. save_prime_list fonksiyonu, hesaplanan asal 
sayıları bir dosyaya kaydeder.
"""
