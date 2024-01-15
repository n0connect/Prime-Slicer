from multiprocessing import Lock, Pool  # Paralel programlama için Lock, ve İşlem havuzu Pool
from tqdm import tqdm   # ProcessBar
import multiprocessing  # Paralel programlama
import math
import pickle
import os
import sys
import time
import gc   # Manuel Bellek Temizlemek
import configparser  # .ini Dosyası oluşturmak için


# GLOBAL VARIABLES
user_end_number_: int  # Kullanıdan alınan bitiş değerini bellekte tutar.
start_number_: int  # Kullanıdan alınan bailangıç değerini bellekte tutar.
last_digit_ = 0  # Son kaydedilen .pkl dosyasının sayı değerini bellekte tutar.
temp_num_ = 0  # Yüklenilen .pkl dosyasının sayı değerini bellekte tutar.
loaded_list: list  # Kontrol için yüklenen .pkl dosyası bu listede tutulur.
new_created_file_name_: str  # Yeni oluşan yada son kaydedilen .pkl dosyasının ismi.
user_min_value_: int    # Kullanıcının girebileceği min değer

# .ini CONTROL
marginal_error: int = 10     # Karekök ve Algoritmik hatalardan kaçınmak için (default=10)

lock = Lock()   # Paralel çalışan parçacıklar için kilit mekanizması


def clean_memory():
    gc.collect()


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
    global marginal_error

    # Yeni bir ConfigParser nesnesi oluşturun
    config = configparser.ConfigParser()

    # .ini Dosyasına kaydedilebilir str() haline getirmek
    _start_number_ = str(start_number_)
    _user_end_number_ = str(user_end_number_)
    _user_min_value_ = str(user_min_value_)
    _last_digit_ = str(last_digit_)
    _new_created_file_name_ = str(new_created_file_name_)
    _loaded_list = 'saved_prime_list0.pkl'
    _marginal_error = str(marginal_error)

    # 'Settings' bölümünü ekleyin
    config.add_section('Settings')
    config.add_section('Recommended Settings')

    # Değişen değerler
    config.set('Settings', 'start-number', _start_number_)
    config.set('Settings', 'end-number', _user_end_number_)
    config.set('Settings', 'last-calculated-num', _user_min_value_)
    config.set('Settings', 'count-of-pkl', _last_digit_)
    config.set('Settings', 'current-saving-pkl-name', _new_created_file_name_)
    config.set('Settings', 'current-loading-pkl-name', _loaded_list)

    # Önerilen değerler
    config.set('Recommended Settings', 'cpu-count', '4')
    config.set('Recommended Settings', 'chunk-count', '4')
    config.set('Recommended Settings', 'marginal-error', _marginal_error)

    try:
        # .ini dosyasını oluşturun
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    except Exception as ex:
        raise print(f".ini file create error: {ex}")


def read_ini_():
    # .ini dosyasını oku
    global start_number_
    global user_end_number_
    global user_min_value_
    global last_digit_
    global new_created_file_name_
    global marginal_error

    config = configparser.ConfigParser()

    # .ini dosyasını okuyun
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
    global user_end_number_
    global start_number_

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
            user_end_number_ = int(input(f"Enter a ODD last number (default: number>={user_min_value_ + 100}): "))

            if start_number_ <= 0 or user_end_number_ <= 0 or start_number_ >= user_end_number_:
                raise ValueError
            if start_number_ % 2 == 0 or user_end_number_ % 2 == 0:
                raise print("Please Enter two ODD number.")
            if start_number_ < user_min_value_:
                raise print(f"You have already worked in this range >{user_min_value_}")
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
    density_of_primes_ = 100 * (average_prime_ / (user_end_number_-start_number_))

    print(f"Average prime number count between {(start_number_, user_end_number_)}≈ "
          f" {int(average_prime_)}")
    print(f"Density of prime between than {(start_number_, user_end_number_)}≈ %{int(density_of_primes_)}")
    time.sleep(5)  # İncelenmek için 3sn bekler


def load_with_this_value_prime_list():
    global last_digit_
    global loaded_list
    global temp_num_

    try:
        with open(f'saved_prime_list0.pkl', 'rb') as saved_file:
            loaded_list = pickle.load(saved_file)
            return ":)"
    except Exception as ex:
        print(f"\nsaved_prime_list{temp_num_}.pkl file is broken: {ex}")
        print("Please Delete Broken and Empty Files. And Restart The Program")


def information_about_saved_pkl_():
    global new_created_file_name_
    global last_digit_
    global user_min_value_

    for temp_num in range(0, last_digit_ + 1, 1):
        try:
            with open(f'saved_prime_list{temp_num}.pkl', 'rb') as dump_in_terminal:
                dump_list = pickle.load(dump_in_terminal)
                if not dump_list:
                    raise print("_EmptyFile_")
                len_of_list = len(dump_list)
                user_min_value_ = dump_list[-1]
                print(f'saved_prime_list{temp_num}.pkl;')
                print(f"The prime number at the top of the list: {dump_list[0]}")
                print(f"The prime number in the middle of the list: {dump_list[int(len_of_list / 2)]}")
                print(f"The prime number at the end of the list: {dump_list[-1]}")
                print(f"the list contains {len_of_list} prime numbers")
                print("\n")
            dump_in_terminal.close()
        except Exception as ex:
            print(f"saved_prime_list{temp_num}.pkl file is broken: {ex}")
            print("Please Delete Broken and Empty Files. And Restart The Program")
            print("\n")


def kill_the_program():
    # Diğer işlemler
    print("Processing completed successfully.")
    print(":) boom")
    sys.exit()


def crop_the_list(list_: list) -> list:
    global user_end_number_

    sqrt_end = math.sqrt(user_end_number_) + 100

    # Orijinal listeyi değiştirmek yerine yeni bir liste oluştur
    cropped_list = [item for item in list_ if item <= sqrt_end]

    if not cropped_list:
        print("Load another list manually.")
        sys.exit(1)

    return cropped_list


def save_prime_list(list_):
    global new_created_file_name_

    if not list_:
        print("List is empty. No need to save.")
        return

    flat_results = [item for sublist in list_ for item in sublist
                    if item is not None and item <= user_end_number_]

    flat_results = sorted(flat_results)

    try:
        print(f"Saving: {flat_results[:10]}...{flat_results[-3:]}")
        with open(f'{new_created_file_name_}', 'wb') as temp_list:
            pickle.dump(flat_results, temp_list)
        print(f"\nList saved successfully in --> {new_created_file_name_}")
    except Exception as ex:
        print(f"Saving Error: {ex}")


def is_prime(number, primes):
    sqrt_of_num = None

    with lock:
        sqrt_of_num = math.isqrt(number)

    for prime in primes:
        if prime > sqrt_of_num:
            return True
        if number % prime == 0:
            return False
    print(f"Exeption number [PROGRAM CAN NOT DEFİNE IS PRIME OR NOT];"
          f" {number}, RootOfNum: {sqrt_of_num}")
    return False


def worker(chunk, shared_primes):
    try:
        start, end = chunk
        local_results = []

        for number in range(start, end + 2, 2):
            if is_prime(number, shared_primes):
                local_results.append(number)
    except Exception as e:
        # Multiprocessing hatası durumunda programı sonlandır
        print(f"An error occurred in multiprocessing: {e}")
        raise SystemExit

    return local_results


def choose_cpu_count():
    mp_count = multiprocessing.cpu_count()

    print(f"""
    \033[1mIf you're unsure about the optimal choice, consider the following:

    More CPU can lead to Faster processing but might require additional system resources.

    Total CPU count: {mp_count}
    Recommended range: {mp_count // 2} - {mp_count}

    Choose a value based on your system's capabilities:
    - If you have a powerful system, you can experiment with higher values for faster processing.
    - For resource-conscious use, stick to the recommended range or lower.

    Keep in mind that the ideal value may vary based on your specific hardware and workload.\033[0m
    """)

    try:
        mp_count = multiprocessing.cpu_count()
        print(f"\nTotal CPU count: {mp_count}")

        while True:
            cpu_count_ = int(input("Enter the number of CPUs to use for the process: "))

            if cpu_count_ < mp_count // 2 or cpu_count_ > mp_count:
                raise ValueError(f"Invalid choice! Please enter a value between {mp_count // 2} and {mp_count}.")

            print(f"We are going to use {cpu_count_} CPUs for the process.")
            return cpu_count_

    except ValueError as ve:
        print(f"Error: {ve}")
        print("Please enter a valid integer between the recommended range.")
        return choose_cpu_count()

    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        print("Please try again.")
        return choose_cpu_count()


def chose_num_of_chunks():

    print("""
    \033[1mIf you're unsure about the optimal choice, consider the following:

    More CHUNKS can lead to Faster processing but might require additional system resources.
    Fewer CHUNKS might be slower but can be more resource-efficient.

    Recommended Value Range: 4-6

    Choose a value based on your system's capabilities:
    - If you have a powerful system, you can experiment with higher values for faster processing.
    - For resource-conscious use, stick to the recommended range or lower.

    Keep in mind that the ideal value may vary based on your specific hardware and workload.\033[0m
    """)

    try:
        mp_count = multiprocessing.cpu_count()
        print(f"\nTotal CPU count: {mp_count}")

        while True:
            chunk_count = int(input("Enter the number of chunks to divide the task into: "))

            if chunk_count > mp_count or chunk_count <= 0 or chunk_count > 8:
                raise ValueError(f"Invalid choice! Please enter a value between {mp_count // 2} and 8.")

            print(f"We are going to use {chunk_count} chunks to distribute the task.")
            return chunk_count

    except ValueError as ve:
        print(f"Error: {ve}")
        print("Please enter a valid integer between the recommended range.")
        return chose_num_of_chunks()

    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        print("Please try again.")
        return chose_num_of_chunks()


def chunks_grouped(slice_count):
    global start_number_, user_end_number_

    # Listeyi oluştur
    chunk_list = [(i, i + 999) for i in range(start_number_, user_end_number_ + 2, 1000)]

    # Liste parçalanmalarını belirle
    chunk_size = len(chunk_list) // slice_count
    remainder = len(chunk_list) % slice_count

    # chunks elemanlarını her biri slice_count adet gruplar halinde alt listelere böl
    chunks = [chunk_list[i * chunk_size:(i + 1) * chunk_size] for i in range(slice_count)]

    # Eğer remainder varsa, kalanı sonuncu chunk'a ekle
    if remainder:
        chunks[-1] += chunk_list[-remainder:]

    return [tuple(chunk) for chunk in chunks]   # Listeyi dön


def len_of_the_chunk() -> int:
    global start_number_, user_end_number_

    len_of_chunk: int = 0

    for _ in range(start_number_, user_end_number_ + 2, 1000):
        len_of_chunk += 1

    return len_of_chunk


def main() -> None:
    global loaded_list, start_number_

    # Kullanılacak cpu sayısı
    num_processes = choose_cpu_count()

    # Aynı anda işlenecek chunk sayısı (Balanced)
    num_of_chunks = chose_num_of_chunks()

    # Yüklü Asal Sayı Listesini Kırpmak
    cropped_list_ = crop_the_list(loaded_list)

    # Süreyi başlat.
    start_time = time.time()

    # Parçalanacak aralığın uzunluğunu bul
    len_of_chunks: int = len_of_the_chunk()

    # Paralel işlemeye başla.
    with Pool(processes=num_processes) as pool:
        # Her bir chunk grubunun max(num_of_chunks) listesini tutar
        chunk_results = []

        # tqdm ile progress bar oluşturun
        pbar = tqdm(total=len_of_chunks, desc="Processing Chunks", position=0, leave=True)

        # chunks_grouped(list, division-num) ile liste division-num'er Chunk olacak şekilde parçalanır
        # Parçalanmış chunks listesini alt(num_of_chunks) parçalara böl
        for chunk_group in chunks_grouped(num_of_chunks):

            if not len(chunk_group):
                continue  # Liste boşsa ya da verilen sınırın dışında ise sırada ki elemanı dene.

            # Hata ayıklama bloğu
            try:
                # chunk_group tuplesi paralel aSencron işlenir
                results_list = [
                    pool.apply_async(worker, args=(chunk, cropped_list_), callback=lambda _: pbar.update(1))
                    for chunk in chunk_group
                ]

            except Exception as e:
                # Multiprocessing hatası durumunda programı sonlandır
                print(f"An error occurred in multiprocessing: {e}")
                raise SystemExit

            # Sonuçları toplamak için bekleyin
            chunk_results += [result.get() for result in results_list]

            save_prime_list(chunk_results)  # Chunk Kaydet
            chunk_results = []  # Listeyi boşalt
            # Manuel Bellek Temizliği.
            clean_memory()

        # İşlem tamamlandığında None değer ve alt listeler silinir
        flat_results = [item for sublist in chunk_results for item in sublist
                        if item is not None and item <= user_end_number_]

    # Sıralanmış liste
    final_results = sorted(flat_results)

    # Manuel Bellek Temizliği.
    clean_memory()

    # Sıralanmış listenin bir kısmı
    print(f"Final Result: {final_results[:5]}...{final_results[-5:]}")

    # Listeyi kaydet.
    save_prime_list(flat_results)

    # Manuel Bellek Temizliği.
    clean_memory()

    # Toplam çalışma süresi
    finish_time = time.time()
    print(f"Total Calc. Time: {finish_time - start_time} second(s) / "
          f"{(finish_time - start_time)/60} minute")

    # Bilgi ver.
    information_about_saved_pkl_()
    kill_the_program()


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
