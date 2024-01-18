from multiprocessing import Lock, Pool  # Lock:Senkronizasyon Pool:İşlemHavuzu Manager:PaylaşımlıListe
import multiprocessing  # Paralel programlama işlemleri için kullandığım modül.
import numpy as np  # numPy ile optimizasyon.
from tqdm import tqdm  # ProcessBar oluşturmak için kullandığım modül.
import configparser  # .ini Dosyası oluşturmak için kullandığım modül.
import pickle  # Belirlenen asal sayıları kaydedip, yükleyen modül.
import os  # Windows üzerinde işlemler gerçekleştiren modül.
import sys  # Sistem üzerinde işlemler gerçekleştiren modül.
import time  # Zaman kontolünü sağlayan modül.

# GLOBAL VARIABLES
user_end_number_: int  # Kullanıdan alınan bitiş değerini bellekte tutar.
start_number_: int  # Kullanıdan alınan bailangıç değerini bellekte tutar.
last_digits_list_ = []  # Son kaydedilen .pkl dosyalarının sayı değerini bellekte tutar.
last_digit_ = 0  # Son kaydedilen .pkl dosyasının sayı değerini bellekte tutar.
temp_num_ = 0  # Yüklenilen .pkl dosyasının sayı değerini bellekte tutar.
loaded_list: list  # Kontrol için yüklenen .pkl dosyası bu listede tutulur.
new_created_file_name_: str  # Yeni oluşan yada son kaydedilen .pkl dosyasının ismi.
loaded_prime_list_name: str  # Asal sayı kontrolünü yapacak liste belirlenir.
user_min_value_: int  # Kullanıcının girebileceği min başlangıç değeri.
marginal_error: int = 100  # Karekök ve Algoritmik hatalardan kaçınmak için (default=100)
chunk_range: int  # İki chunk elemanı arasında ki uzaklık. (a, b) => b-a = chunk_range
num_processes: int  # Kullanılacak işlemci sayısı
num_of_chunks: int  # Kullanılacak Chunk sayısı

lock = Lock()  # Paralel çalışan parçacıklar için kilit mekanizması


def start_program():
    file_size_control()
    take_user_number()
    ini_file_update()
    read_ini_file()
    approx_calculation_of_probability()
    load_with_this_value_prime_list()


def file_size_control():
    # Program ilk çalıştığında kaydedilen .pkl dosyalarını kontrol eder
    global new_created_file_name_
    global last_digit_

    try:
        print(f"_" * 60)  # FOR GOOD SEEN
        saved_files_list = os.listdir(os.getcwd())  # Dizinde ki dosyaları al

        for file in saved_files_list:
            if file.endswith('.pkl'):  # .pkl olanları seç

                remove_character_in_file_name(file)  # Son kaydedilen sayıyı al ör:5
                print(f"Saved Prime list {file}: {os.stat(file).st_size / (1024 ** 2)} MB")  # Boyut Kontrolü
                print(f"_" * 60)  # Sadece görsellik için

        last_digit_ = int(max(last_digits_list_))
        last_saved_file = f'saved_prime_list{last_digit_}.pkl'

        if 20 <= os.stat(last_saved_file).st_size / (1024 ** 2):  # Boyutu 20MB fazla ise

            print(f"{last_saved_file:>30} size is max.")
            print(f"_" * 60)
            new_created_file_name_ = f'saved_prime_list{last_digit_ + 1}.pkl'  # Yeni .pkl dosyası 6 olur
            create_new_pkl_file_()  # yeni .pkl oluştur
        else:

            new_created_file_name_ = f'{last_saved_file}'  # Son .pkl ile işleme devam edilir ör:5

        # Dosyalar Hakkında Bilgi Yazdırmak
        information_about_saved_pkl_()

    except Exception as ex:
        raise print(f"{ex}")


def ini_file_update():
    # Eğer .ini yoksa oluşturur
    global start_number_, user_end_number_, user_min_value_
    global last_digit_, new_created_file_name_, loaded_prime_list_name
    global marginal_error, chunk_range, num_processes, num_of_chunks

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
        # Eğer .ini yoksa
        choose_cpu_count()  # Kullanılacak cpu sayısını seç
        chose_num_of_chunks()  # Aynı anda işlenecek chunk sayısı (Balanced)
        chose_range_of_chunks()  # Chunk'ların aralığını belirler.

        config.add_section('Settings')
        config.add_section('Recommended Settings')

        # Değişen değerleri oluştur
        config.set('Recommended Settings', 'marginal-error', '50')
        config.set('Recommended Settings', 'chunk-range', str(chunk_range))
        config.set('Recommended Settings', 'cpu-count', str(num_processes))
        config.set('Recommended Settings', 'chunk-count', str(num_of_chunks))
        config.set('Settings', 'current-loading-pkl-name', 'saved_prime_list0.pkl')

        # Gerekli set fonksiyonlarını çağır

    config.read(config_file)  # .ini dosyasını oku

    # Değiştirilebilir değerler .ini içerisinden ayarlanabilir değerler
    _loaded_prime_list_name = config.get('Settings', 'current-loading-pkl-name')
    _chunk_range = config.get('Recommended Settings', 'chunk-range')
    _cpu_count = config.get('Recommended Settings', 'cpu-count')
    _chunk_count = config.get('Recommended Settings', 'chunk-count')
    _marginal_error = config.get('Recommended Settings', 'marginal-error')

    # Değişen değerler
    config.set('Settings', 'start-number', _start_number_)
    config.set('Settings', 'end-number', _user_end_number_)
    config.set('Settings', 'last-calculated-num', _user_min_value_)
    config.set('Settings', 'count-of-pkl', _last_digit_)
    config.set('Settings', 'current-saving-pkl-name', _new_created_file_name_)
    config.set('Settings', 'current-loading-pkl-name', _loaded_prime_list_name)

    # Önerilen değerler
    config.set('Recommended Settings', 'cpu-count', _cpu_count)
    config.set('Recommended Settings', 'chunk-count', _chunk_count)
    config.set('Recommended Settings', 'chunk-range', _chunk_range)
    config.set('Recommended Settings', 'marginal-error', _marginal_error)

    try:
        # .ini dosyasını oluşturun
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    except configparser.ParsingError as ex:
        print(f"Error parsing .ini file: {ex}")
    except Exception as es:
        print(f"Error updating .ini file: {es}")


def read_ini_file():
    global start_number_, user_end_number_, user_min_value_
    global last_digit_, new_created_file_name_, loaded_prime_list_name
    global chunk_range, marginal_error, num_processes, num_of_chunks

    # .ini dosyasını oku
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
    _chunk_range = config.get('Recommended Settings', 'chunk-range')
    _chunk_count = config.get('Recommended Settings', 'chunk-count')
    _cpu_count = config.get('Recommended Settings', 'cpu-count')

    # Değerler ile eşleştir
    start_number_ = int(_start_number_)
    user_end_number_ = int(_user_end_number_)
    user_min_value_ = int(_user_min_value_)
    last_digit_ = int(_last_digit_)
    chunk_range = int(_chunk_range)
    num_processes = int(_cpu_count)
    num_of_chunks = int(_chunk_count)
    new_created_file_name_ = _new_created_file_name

    # Değiştirilebilir değerleri yükle.
    loaded_prime_list_name = _loaded_list_
    marginal_error = int(_marginal_error)


def choose_cpu_count():
    global num_processes

    mp_count = multiprocessing.cpu_count()

    print(f"_" * 60)
    print(f"""
    If you're unsure about the optimal choice, consider the following:
    More CPU can lead to Faster processing but might require additional system resources.

    Choose a value based on your system's capabilities:
    \033[1m- If you have a powerful system, you can experiment with higher values for faster processing.
    - For resource-conscious use, stick to the recommended range or lower.\033[0m

    Keep in mind that the ideal value may vary based on your \033[1m"specific hardware"\033[0m and workload.

    \033[1mTotal CPU count: {mp_count}
    Recommended range: [{mp_count // 2}, {mp_count}]\033[0m
    """)
    print(f"_" * 60)

    try:
        mp_count = multiprocessing.cpu_count()

        while True:
            num_processes = int(input("Enter the number of CPUs to use for the process: "))
            num_processes = max(num_processes, mp_count // 2)  # min cpu kullanıcıya göre seç
            if num_processes < mp_count // 2 or num_processes > mp_count:
                raise ValueError(f"Invalid choice! Please enter a value between {mp_count // 2} and {mp_count}.")
            print(f"_" * 60)
            print(f"\033[1mWe are going to use {num_processes} CPUs for the process.\033[0m")
            time.sleep(2)  # incelemek için
            break

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
    global num_of_chunks

    print(f"_" * 60)
    print("""
    If you're unsure about the optimal choice, consider the following:

    More CHUNKS can lead to Faster processing but might require additional system resources.
    Fewer CHUNKS might be slower but can be more resource-efficient.

    \033[1mChoose a value based on your system's capabilities:
    - If you have a powerful system, you can experiment with higher values for faster processing.
    - For resource-conscious use, stick to the recommended range or lower.\033[0m

    Keep in mind that the ideal value may vary based on your \033[1m"specific hardware"\033[0m and workload.

    Recommended Value Range: \033[1m[4, 10]\033[0m
    Max Value Range: \033[1m20\033[0m
    """)
    print(f"_" * 60)
    try:
        mp_count = multiprocessing.cpu_count()

        while True:
            num_of_chunks = int(input("\033[1mEnter the number of chunks to divide the task into: \033[0m"))
            num_of_chunks = max(num_of_chunks, 4)  # Kullanıcının seçimini min 4 olarak seç
            if num_of_chunks > mp_count or num_of_chunks <= 0 or num_of_chunks > 20:
                raise ValueError(f"Invalid choice! Please enter a value between {mp_count // 2} and 8.")

            print(f"\033[1mWe are going to use {num_of_chunks} chunks to distribute the task.\033[0m")
            print(f"_" * 60)
            time.sleep(2)  # İncelemek için.
            break

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


def chose_range_of_chunks():
    global chunk_range

    print("""
    \033[1mWhen using the program,
    the intervals between the two entered numbers are divided into chunks based on the range you provide.

    To optimize the program's performance, it is recommended to choose an even number for the chunk range
    that is appropriate for your hardware. Make sure to enter an even chunk range to ensure the best results.
    By increasing the range of chunks processed in parallel, each thread can perform more work, resulting
    in a more efficient process. It is important to note that the total amount of work done with the specified
    Chunk Range remains the same. However, this approach can help distribute the workload more evenly among workers,
    avoiding overburdening any individual worker.\033[0m

    Recommended Value's: {1000, 2000, 3000, 4000, 5000}
    """)

    while True:
        try:
            chunk_range = int(input("Enter the chunk range (default: \033[1m1000\033[0m): "))
            if chunk_range % 2 != 0 or chunk_range <= 0 or chunk_range < 1000:
                print("""
                Please enter a valid number that meets the specified conditions.
                If you do not know what you are doing, continue with the default value
                """)
                raise ValueError
            print(f"_" * 60)
            print(f"\033[1mWe are going to use {chunk_range} distribute the chunk's.\033[0m")
            break  # Doğru ise döngüyü kır
        except Exception as ex:
            print(f"Exception Error: {ex}")


def remove_character_in_file_name(last_saved_file):
    global last_digits_list_

    # Kaç tane .pkl dosyasının kayıtlı olduğu sayısıdır.
    digits = ''.join(char for char in last_saved_file if char.isdigit())
    last_digits_list_.append(int(digits))


def create_new_pkl_file_():
    # 1MB aşan dosya varsa bu fonksiyon yeni bir .pkl oluşturur.
    global last_digit_

    try:
        with open(f'saved_prime_list{last_digit_ + 1}.pkl', 'wb') as my_new_pkl:
            print(f"Created New .PKL: saved_prime_list{last_digit_ + 1}")
            my_new_pkl.close()
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
    global user_end_number_, start_number_, num_processes

    average_prime_ = (user_end_number_ / np.log(user_end_number_)) - (start_number_ / np.log(start_number_))
    density_of_primes_ = 100 * (average_prime_ / (user_end_number_ - start_number_))
    print(f"_" * 60)
    print(f"\033[1mAverage prime number count between ≈ {int(average_prime_)}\033[1n")
    print(f"\033[1mDensity of prime between than ≈ %{int(density_of_primes_)}\033[1n")
    print(f"_" * 60)
    print(f"\033[1mWe are going to use {num_processes} CPUs for the process.\033[0m")
    print(f"\033[1mWe are going to use {num_of_chunks} chunks to distribute the task.\033[0m")
    print(f"\033[1mWe are going to use {chunk_range} distribute the chunk's.\033[0m")
    print(f"_" * 60)
    time.sleep(7)  # İncelenmek için 7sn bekler


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

    for temp_num in range(0, (last_digit_ + 2)):
        try:
            with open(f'saved_prime_list{temp_num}.pkl', 'rb') as dump_in_terminal:
                dump_list = pickle.load(dump_in_terminal)

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
            print("\033[1m_EmptyFile_\033[1n")
            print(f"_" * 60)
    print(f"\033[1mTotal number of calculated primes in the saved .pkl files: {total_primes_}\033[1n")


def crop_the_list(list_: list):
    global user_end_number_
    global marginal_error

    sqrt_end = np.sqrt(user_end_number_).astype(int) + marginal_error

    # Özel bir hata mesajı fırlatır
    if not sqrt_end <= list_[-1]:
        print(f"""\033[1m
            Since the square root of {sqrt_end}, the last number you selected,
            is greater than the last element of 'saved_prime_list0.pkl', the list
            that tests for prime numbers, the process is terminated.

            Solution: Load a larger prime checklist or merge two prime lists :)\033[1n
            """)
        sys.exit(1)

    # Performans için dtype ile dizeyi optimum boyutta tutar
    optimum_list = np.array(list_)
    optimum_list = optimum_list[optimum_list <= sqrt_end]

    return optimum_list


def save_prime_list(list_):

    global new_created_file_name_

    if not list:
        print("List is empty. No need to save.")
        return

    try:
        # Liste içinde listeler yapısını düzleştir.
        flat_results = [item for sublist in list_ for item in sublist
                        if item is not None and item <= user_end_number_]

        # aSencron kaydedilen Asal sayılar sıralanır.
        flat_results = sorted(flat_results)

        with open(f'{new_created_file_name_}', 'wb') as temp_list:
            pickle.dump(flat_results, temp_list)

    except Exception as ex:
        print(f"Saving Error: {ex}")


def chunks_grouped(slice_count):

    global start_number_, user_end_number_, chunk_range

    try:
        # Listeyi oluştur
        chunk_list = [(i, i + chunk_range) for i in range(start_number_, user_end_number_ + 2, chunk_range)]

        # Liste parçalanmalarını belirle
        chunk_size = len(chunk_list) // slice_count

        # chunks elemanlarını her biri slice_count adet gruplar halinde alt listelere böl
        chunks = [chunk_list[i * slice_count:(i + 1) * slice_count] for i in range(chunk_size + 1) if
                  len(chunk_list[i * slice_count:(i + 1) * slice_count]) > 0 or i * slice_count >= chunk_size]

    except Exception as ex:
        print(f"An error in group function: {ex}")
        sys.exit(1)

    return [tuple(chunk) for chunk in chunks]  # Listeyi dön


def len_of_the_chunk() -> int:
    # ProgresBar için gerekli total burada belirlenir.
    global start_number_, user_end_number_, chunk_range

    len_ = len(np.arange(start_number_, user_end_number_ + 2, chunk_range))

    return len_


def is_prime(number, primes):

    try:
        sqrt_of_num = 100 + np.sqrt(number).astype(int)   # marginal-error

        # Bölünürse asal değildir False, aksi halde True
        presence_of_divisors = np.any(np.mod(number, primes[primes <= sqrt_of_num]) == 0)

    except Exception as ex:
        print(f"An error in prime function: {ex}")
        sys.exit(1)

    return ~presence_of_divisors  # ~0=1


def worker(args, shared_primes):
    try:
        # Gönerilen aralık oluşturulur ve paralel işlenir
        start, end = args

        # Dizeyi kıstır
        numbers = np.arange(start, end + 2, 2)

        # Kontrol Vektörler ile gerçekleşir; Her x: için bir maske oluşturur;
        is_prime_mask = np.vectorize(lambda x: is_prime(x, shared_primes))(numbers)

        # Maskesinde asal etiketi olanları alır.
        local_results = numbers[is_prime_mask]

    except Exception as e:
        print(f"An error occurred in multiprocessing in worker function: {e}")
        raise SystemExit
    return local_results  # Her işçi kendi local listesini döndürür.


def main() -> None:
    global loaded_list, start_number_
    global num_processes, num_of_chunks

    cropped_list_ = crop_the_list(loaded_list)  # Yüklü Asal Sayı Listesini Kırpmak
    len_of_chunks: int = len_of_the_chunk()  # Parçalanacak aralığın uzunluğunu bul

    start_time = time.time()  # Süreyi başlat.

    # Parallel işlemeye başla.
    with Pool(processes=num_processes) as pool:
        chunk_results = []
        pbar = tqdm(total=len_of_chunks, desc="Processing Chunks", position=0, leave=True)  # progress bar oluştur

        # Parçalanmış chunks listesini alt(num_of_chunks) parçalara böl
        for chunk_group in chunks_grouped(num_of_chunks):

            try:
                # chunk_group tuplesi paralel aSencron işlenir
                results_list = [
                    pool.apply_async(worker, args=(chunk, cropped_list_), callback=lambda _: pbar.update(1))
                    for chunk in chunk_group
                ]

                # Sonuçları toplamak için bekleyin
                chunk_results += [result.get() for result in results_list]

            except Exception as e:
                print(f"An error occurred in multiprocessing in main function: {e}")
                raise SystemExit
            except KeyboardInterrupt:
                sys.exit(0)  # CTRL + C SONLANDIR

    finish_time = time.time()   # Toplam çalışma süresi
    ex_time = time.time()  # Saving işlem süresi
    save_prime_list(chunk_results)  # Hesaplanan asalları kaydet
    information_about_saved_pkl_()  # Bilgi ver.
    xe_time = time.time()  # Saving işlem süresi

    print(f'ChunkResults: {chunk_results[:10]}...{chunk_results[-10:]}')

    print(f"\033[1mTotal Calc. Time of Multiprocessing: {finish_time - start_time} second(s) / "
          f"{(finish_time - start_time) / 60} minute\033[1n")

    print(f"\033[1mTotal Calc. Time of Program: {finish_time + xe_time - start_time - ex_time} second(s) / "
          f"{(finish_time + xe_time - start_time - ex_time) / 60} minute\033[1n")

    kill_the_program()  # Programı sonlandır


def kill_the_program():
    # Diğer işlemler
    print("Processing completed successfully.")
    print("\033[1m WabaLabaDubDub \033[0m")
    print("\033[1m:) boom\033[1n")
    sys.exit(0)


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
