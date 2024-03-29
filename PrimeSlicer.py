from multiprocessing import Lock, Pool  # Lock:Senkronizasyon Pool:İşlemHavuzu Manager:PaylaşımlıListe
import multiprocessing  # Paralel programlama işlemleri için kullandığım modül.
import numpy as np  # numPy ile optimiznumasyon.
from tqdm import tqdm  # ProcessBar oluşturmak için kullandığım modül.
import configparser  # .ini Dosyası oluşturmak için kullandığım modül.
import pickle  # Belirlenen asal sayıları kaydedip, yükleyen modül.
import os  # Windows üzerinde işlemler gerçekleştiren modül.
import shutil  # Terminal boyutunu ileten modül.
import sys  # Sistem üzerinde işlemler gerçekleştiren modül.
import time  # Zaman kontolünü sağlayan modül.

# GLOBAL VARIABLES
end_user_number: int  # Kullanıdan alınan bitiş değerini bellekte tutar.
start_user_number: int  # Kullanıdan alınan bailangıç değerini bellekte tutar.
file_digits_list = []  # Son kaydedilen .pkl dosyalarının sayı değerini bellekte tutar.
last_file_digit = 0  # Son kaydedilen .pkl dosyasının sayı değerini bellekte tutar.
temp_num_ = 0  # Yüklenilen .pkl dosyasının sayı değerini bellekte tutar.
loaded_list: list  # Kontrol için yüklenen .pkl dosyası bu listede tutulur.
new_file_name: str  # Yeni oluşan yada son kaydedilen .pkl dosyasının ismi.
loaded_prime_list_name: str  # Asal sayı kontrolünü yapacak liste belirlenir.
user_min_value_: int  # Kullanıcının girebileceği min başlangıç değeri.
marginal_error: int = 100  # Karekök ve Algoritmik hatalardan kaçınmak için (default=100)
chunk_range: int = 1000  # İki chunk elemanı arasında ki uzaklık. (a, b) => b-a = chunk_range
num_processes: int = 4  # Kullanılacak işlemci sayısı
num_of_chunks: int = 4  # Kullanılacak Chunk sayısı

lock = Lock()  # Paralel çalışan parçacıklar için kilit mekanizması


def start_program():
    file_size_control()
    take_user_number()
    ini_file_update()
    read_ini_file()
    approx_calculation_of_probability()
    load_with_this_value_prime_list()


def terminal_options(outputs, error_message_list):
    try:
        # Önce os modülünü dene.
        terminal_width, _ = os.get_terminal_size()
    except OSError:
        try:
            # Olmazsa shutil modülünü dene.
            terminal_width, _ = shutil.get_terminal_size()
        except Exception as ex:
            # Her iki durumda da başarısız olursa hata mesajını yazdır
            print(f"Terminal size detection error: {ex}")
            terminal_width = 80  # Default bir değer atayarak işlemlere devam et.

    break_point = terminal_width // 2  # Kesme noktası.

    # Tuple içermeyen bir liste ise.
    if not any(isinstance(item, tuple) for item in outputs):
        formatted_outputs = []

        for i in range(0, len(outputs) + 1, 2):
            if i < len(outputs):
                output1 = outputs[i][:break_point].ljust(break_point)

                if i + 1 < len(outputs):
                    output2 = outputs[i + 1][:break_point].ljust(break_point)
                    extract_tuple = (output1, output2)
                    formatted_outputs.append(extract_tuple)
                else:
                    extract_tuple = (output1, '')
                    formatted_outputs.append(extract_tuple)

        for formatted_one, formatted_two in formatted_outputs:
            print(formatted_one + formatted_two)
            print("_" * terminal_width)

    # Tuple içeren bir liste ise.
    else:
        for index in range(0, len(outputs) + 1, 2):
            if index < len(outputs):
                # Yüklenen Dosya bilgilerini al.
                output1 = outputs[index][0][:break_point].ljust(break_point)

                # Ilk elemanın içinde ki bilgileri al.
                data_one_output1 = outputs[index][1][0][:break_point].ljust(break_point)
                data_two_output1 = outputs[index][1][1][:break_point].ljust(break_point)
                data_three_output1 = outputs[index][1][2][:break_point].ljust(break_point)

                # Yüklenen ikinci Dosya bilgilerini al.
                if index + 1 < len(outputs):
                    # Tuplenin ikinci elemanını al.
                    output2 = outputs[index + 1][0][:break_point].ljust(break_point)

                    # Ikinci elemanın içinde ki bilgileri al.
                    data_one_output2 = outputs[index + 1][1][0][:break_point].ljust(break_point)
                    data_two_output2 = outputs[index + 1][1][1][:break_point].ljust(break_point)
                    data_three_output2 = outputs[index + 1][1][2][:break_point].ljust(break_point)

                    # Terminalde düzenli yazdır.
                    print(output1 + output2), print(data_one_output1 + data_one_output2)
                    print(data_two_output1 + data_two_output2), print(data_three_output1 + data_three_output2)
                    print("_" * terminal_width)
                else:
                    print(output1), print(data_one_output1), print(data_two_output1)
                    print(data_three_output1), print("_" * terminal_width)

    if len(error_message_list) > 0:
        for err_mesage in error_message_list:
            print(f'Significant Error: {err_mesage}')

    print('\n')  # NewLine
    time.sleep(3)  # Terminal geçikmesini önlemek için bekletir.


def file_size_control():
    # Program ilk çalıştığında kaydedilen .pkl dosyalarını kontrol eder
    global new_file_name
    global last_file_digit, file_digits_list

    file_size_outputs = []

    try:

        saved_files_list = os.listdir(os.getcwd())  # Dizinde ki dosyaları al

        # Dosya isimlerini sayısal sıraya göre sırala
        saved_files_list = sorted([file for file in saved_files_list if file.endswith('.pkl')],
                                  key=lambda x: int(x.split('.')[0].split('saved_prime_list')[-1]))
        # ('.').[0] nokta da dahil sonrasını, ('saved_prime_list')[-1]

        for file in saved_files_list:
            # Son kaydedilen sayıyı al file_digits_list kaydet
            remove_character_in_file_name(file)
            # Dosyaların Boyut Kontrolü '\u00AC' sembolik bir ifadedir.
            file_save_string = f'\u00AC {file}: {os.stat(file).st_size / (1024 ** 2):.4} MB'
            # Terminalde yazdırmak için kaydet
            file_size_outputs.append(file_save_string)

        last_file_digit = int(max(file_digits_list))
        last_saved_file = f'saved_prime_list{last_file_digit}.pkl'

        # Kayıt dosyasının boyutu 20MB fazla ise yeni bir kayıt dosyası oluştur.
        if 20 <= os.stat(last_saved_file).st_size / (1024 ** 2):
            print(f"\n{last_saved_file:>40} size is max.\n")

            # Yeni .pkl dosyası ismi oluşturur.
            new_file_name = f'saved_prime_list{last_file_digit + 1}.pkl'

            # yeni .pkl oluştur
            new_logger_for_pickles()

        else:
            new_file_name = f'{last_saved_file}'  # Son .pkl ile işleme devam edilir ör:5

        # Kaydedilen Boyut bilgilerini Terminalde Bastır.
        terminal_options(file_size_outputs, [])

        # Kayıtlı Dosyalar Hakkında Bilgi Yazdırmak
        details_of_stored_pkl_below()

    except Exception as ex:
        print(f'Important Name Err: {ex} \
            Check the Name of .pkl files!')
        raise SystemExit


def ini_file_update():
    # Eğer .ini yoksa oluşturur
    global start_user_number, end_user_number, user_min_value_
    global last_file_digit, new_file_name, loaded_prime_list_name
    global marginal_error, chunk_range, num_processes, num_of_chunks

    # Config nesnesi oluşturulur
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    # .ini dosyasının varlığını kontrol eder
    ini_is_alive = os.path.exists(config_file)

    # .ini Dosyasına kaydedilebilir formata getirmek
    _start_number_ = str(start_user_number)
    _user_end_number_ = str(end_user_number)
    _user_min_value_ = str(user_min_value_)
    _last_digit_ = str(last_file_digit)
    _new_created_file_name_ = str(new_file_name)

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
    global start_user_number, end_user_number, user_min_value_
    global last_file_digit, new_file_name, loaded_prime_list_name
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
    start_user_number = int(_start_number_)
    end_user_number = int(_user_end_number_)
    user_min_value_ = int(_user_min_value_)
    last_file_digit = int(_last_digit_)
    chunk_range = int(_chunk_range)
    num_processes = int(_cpu_count)
    num_of_chunks = int(_chunk_count)
    new_file_name = _new_created_file_name

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

        while True:

            num_processes = int(input("Enter the number of CPUs to use for the process: "))

            if num_processes < mp_count // 2 or num_processes > mp_count:
                raise ValueError(f"Invalid choice! Please enter a value between {mp_count // 2} and {mp_count}.")
            print(f"_" * 60)
            print(f"\033[1mWe are going to use {num_processes} CPUs for the process.\033[0m")
            time.sleep(2)  # incelemek için bekler.
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

    Recommended Value Range: \033[1m[4, 50]\033[0m
    Max Value Range: \033[1m50\033[0m
    """)
    print(f"_" * 60)
    try:
        mp_count = multiprocessing.cpu_count()

        while True:
            num_of_chunks = int(input("\033[1mEnter the number of chunks to divide the task into: \033[0m"))
            num_of_chunks = max(num_of_chunks, 4)  # Kullanıcının seçimini min 4 olarak seç
            if num_of_chunks > mp_count or num_of_chunks <= 0 or num_of_chunks > 50:
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
    global file_digits_list

    # Kaç tane .pkl dosyasının kayıtlı olduğu sayısıdır.
    digits = ''.join(char for char in last_saved_file if char.isdigit())
    file_digits_list.append(int(digits))


def new_logger_for_pickles():
    # 20MB aşan dosya varsa bu fonksiyon yeni bir .pkl oluşturur.
    global last_file_digit

    try:
        with open(f'saved_prime_list{last_file_digit + 1}.pkl', 'wb') as my_new_pkl:
            my_new_pkl.close()
    except Exception as ex:
        print(f"saved_prime_list{last_file_digit + 1}.pkl is not created: {ex}")


def take_user_number():
    global end_user_number, start_user_number

    print("""
    This program has been developed with a new algorithm to find prime numbers faster,
    the basic principle of this algorithm is to use the prime numbers that exist up to
    a certain range to determine the status of other numbers.

    If you have used the program before ignore the default values, you also need to start
    by giving the starting number and the final number a number larger than the last number
    in the list you calculated.

        \033[1mThis program can be dangerous for your computer if you don't know exactly what you are doing,
        use the recommended Chunk and Cpu values\033[0m
        
    My GitHub Link: https://github.com/n0connect/

    """)
    while True:
        try:

            start_user_number = int(input(f"Enter a ODD positive start number(default: number>={user_min_value_}): "))
            end_user_number = int(input(f"Enter a ODD last number: "))

            if start_user_number <= 0 or end_user_number <= 0 or start_user_number >= end_user_number:
                raise print("Please enter two ODD numbers of the correct size.")

            if start_user_number % 2 == 0 or end_user_number % 2 == 0:
                raise print("Please Enter two ODD number.")

            if start_user_number < user_min_value_:
                raise print(f"You have already worked in this range enter the end number; >{user_min_value_}")

            if end_user_number <= user_min_value_:
                end_user_number = user_min_value_ + 100
                print(f"Default choice for the last number: {user_min_value_ + 10000}")
            break  # Eğer istenilen sayılar girilirse fonksiyonu bitir.
        except ValueError as er:
            print(f"{er}")
        except Exception as ex:
            print(f"{ex}")


def approx_calculation_of_probability() -> None:
    # Yaklaşık Asal Miktarı ve Yoğunluğunu hesaplar
    global end_user_number, start_user_number, num_processes

    try:
        average_prime_ = (end_user_number / np.log(end_user_number)) - (start_user_number / np.log(start_user_number))
        density_of_primes_ = 100 * (average_prime_ / (end_user_number - start_user_number))
        print(f"_" * 60)
        print(f"\033[1mAverage prime number count between ≈ {int(average_prime_)}\033[1n")
        print(f"\033[1mDensity of prime between than ≈ %{int(density_of_primes_)}\033[1n")
        print(f"_" * 60)
        print(f"\033[1mWe are going to use {num_processes} CPUs for the process.\033[0m")
        print(f"\033[1mWe are going to use {num_of_chunks} chunks to distribute the task.\033[0m")
        print(f"\033[1mWe are going to use {chunk_range} distribute the chunk's.\033[0m")
        print(f"_" * 60)
        time.sleep(7)  # İncelenmek için 7sn bekler
    except (Exception, ZeroDivisionError) as err:
        print(f"Approx Calculation Err: {err}")
    except KeyboardInterrupt:
        raise print("Process terminated due to user keyboard input.")


def load_with_this_value_prime_list():
    global last_file_digit
    global loaded_list
    global temp_num_
    global loaded_prime_list_name

    # Belirlenen kontol listesini yükler.
    try:
        with open(loaded_prime_list_name, 'rb') as saved_file:
            loaded_list = pickle.load(saved_file)
            return ":)"
    except Exception as ex:
        print(f"\n{loaded_prime_list_name} file is broken: {ex}")
        print("Important err: Control list is broken.")


def details_of_stored_pkl_below():
    global new_file_name
    global last_file_digit
    global user_min_value_

    total_primes_ = 0  # Toplam hesaplanan Asal Sayı adedi
    data_text_list = []  # Listeler hakkında ki bilgiler Tuple olarak kaydedilir.
    error_mesage_list = []  # Hata veren listelerin mesajları.

    # Listelerin yüklenme durumunu görmek için.
    pbar = tqdm(total=last_file_digit, desc="Loading Lists", position=0, leave=True)

    for temp_num in range(0, (last_file_digit + 2)):

        pbar.update(1)  # Liste yüklendi.
        try:
            with open(f'saved_prime_list{temp_num}.pkl', 'rb') as dump_in_terminal:
                dump_list = pickle.load(dump_in_terminal)

                len_of_list = len(dump_list)
                user_min_value_ = dump_list[-1]
                total_primes_ += len_of_list

                data_text_tuple = (
                    f'saved_prime_list{temp_num}.pkl:',
                    [f"Top of the list: {dump_list[0]}",
                     f"The end of the list: {dump_list[-1]}",
                     f"The list contains {len_of_list} prime"]
                )
                data_text_list.append(data_text_tuple)  # Liste hakkında ki bilgileri ekle.

        except Exception as ex:
            # Kayıt listesi ise hata mesajı yazdırma.
            if last_file_digit <= temp_num:
                continue

            expectation_error = f'saved_prime_list{temp_num}.pkl file is broken: {ex}'
            error_mesage_list.append(expectation_error)

    # Progess Bar işlemini tamamladı devredışı olsun ve bulunduğu satırı silsin.
    pbar.close()
    print(rf'{" " * 50}')

    # Dosyalar tamamen açıldığında bilgileri ekrana bastır.
    terminal_options(data_text_list, error_mesage_list)
    print(f"\033[1mTotal number of calculated primes in the saved .pkl files: {total_primes_}\033[1n")


def crop_the_list():
    # Kontrol listesini girilen aralıktaki
    # en büyük (end_user_number) sayının Karekökü ile sınırlar.
    global end_user_number, marginal_error
    global loaded_list

    sqrt_end = np.sqrt(end_user_number).astype(int) + marginal_error

    # Özel bir hata mesajı fırlatır
    if not sqrt_end <= loaded_list[-1]:
        print(f"""\033[1m
            Since the square root of {sqrt_end}, the last number you selected,
            is greater than the last element of 'saved_prime_list0.pkl', the list
            that tests for prime numbers, the process is terminated.

            Solution: Load a larger prime checklist or merge two prime lists :)\033[1n
            """)
        sys.exit(1)

    # Performans için numpy array ile dizeyi optimum boyutta tutar.
    optimum_list = np.array(loaded_list)
    optimum_list = optimum_list[optimum_list <= sqrt_end]

    return optimum_list


def save_prime_list(_chunk_results):

    # Eğer kaydedilecek listede eleman yok ise.
    if not len(_chunk_results) > 0:
        print("List is empty. No need to save.")
        return

    # Liste içinde listeler yapısını düzleştir;
    # Işçilerin özel listelerini içerir.
    flat_results = [item for sublist in _chunk_results for item in sublist
                    if item is not None and item <= end_user_number]

    # aSencron kaydedilen Asal sayılar sorted ile sıralanır.
    flat_results = sorted(flat_results)

    try:
        with open(new_file_name, 'rb') as data:
            exist_data = pickle.load(data)

    except (FileNotFoundError, EOFError) as err:
        # Kayıt listesini açarken bir hata oluşursa; Yüklenen liste boştur.
        print(f"Saving list has an error: {err}\nSaving just calculated list...")
        import_into_pkl_list(flat_results)
        return

    # Kayıt listesinin içinde ki verinin tipini öğren.
    # NumPy array ise eğer; Listeleri NumPy methodu ile sıkıştır.
    if isinstance(exist_data, np.ndarray):
        flat_results = np.array(flat_results)
        _numpy_merged_list = np.concatenate((exist_data, flat_results))
        import_into_pkl_list(_numpy_merged_list)
        return

    # Python listesi ise Python listesi olarak kaydet.
    elif isinstance(exist_data, list):
        merged_list = exist_data + flat_results
        import_into_pkl_list(merged_list)
        return

    else:
        print('Current saving file is not broken or empty, but is not LIST.')
        print(f'Data type is: {type(exist_data)}')
        raise SystemExit


def import_into_pkl_list(save_list):
    # Kaydedilecek dosyanın ismidir; config.ini üzerinden set edilebilir.
    # Otomatik olarak belirlenir.
    global new_file_name

    try:

        with open(new_file_name, 'wb') as data:
            pickle.dump(save_list, data)

    except Exception as ex:
        print(f'Saving Err: {ex}')


def len_of_chunks():
    global start_user_number, end_user_number, num_of_chunks, chunk_range

    # Belirtilen aralığı oluştur ve uzunluğunu bul. ProgessBar için gerekli.
    _chunk_list = [(i, i + chunk_range) for i in range(start_user_number, end_user_number + 2, chunk_range)]

    return len(_chunk_list)


def chunks_grouped(slice_count):
    global start_user_number, end_user_number
    global chunk_range

    try:
        # Listeyi oluştur
        chunk_list = [(i, i + chunk_range) for i in range(start_user_number, end_user_number + 2, chunk_range)]

        # Liste parçalanmalarını belirle
        chunk_size = len(chunk_list) // slice_count

        # chunks elemanlarını her biri slice_count adet gruplar halinde alt listelere böl
        chunks = [chunk_list[i * slice_count:(i + 1) * slice_count] for i in range(chunk_size + 1) if
                  len(chunk_list[i * slice_count:(i + 1) * slice_count]) > 0 or i * slice_count >= chunk_size]

    except Exception as ex:
        print(f"An error in group function: {ex}")
        sys.exit(1)

    return [tuple(chunk) for chunk in chunks]  # Listeyi dön


def is_prime(number, primes):

    sqrt_number = np.sqrt(number+marginal_error).astype(int)

    # Bölünürse asal değildir False, aksi halde True
    presence_of_divisors = np.any(np.mod(number, primes[primes <= sqrt_number]) == 0)

    return ~presence_of_divisors  # ~0=1


def worker(args, shared_primes):
    try:
        # Gönerilen aralık oluşturulur ve paralel işlenir.
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
    global loaded_list, start_user_number
    global num_processes, num_of_chunks

    cropped_list_ = crop_the_list()  # Yüklü Asal Sayı Listesini Kırpmak.
    len_of_chunk = len_of_chunks()  # Listenin uzunluğunu bellekte tutmak için.
    start_time = time.time()  # Süreyi başlat.

    with Pool(processes=num_processes) as pool:
        # Işçi sonuçlarını kalıcı olarak tutan dizedir.
        chunk_results = []

        # progress bar oluştur işçilerin süreçlerini kontrol et.
        pbar = tqdm(total=len_of_chunk, desc="Processing Chunks", position=0, leave=True)

        # Parçalanmış chunks listesini alt (num_of_chunks) adet parçalara böl
        for chunk_group in chunks_grouped(num_of_chunks):
            try:
                # chunk_group tuplesi paralel aSencron işlenir
                results_list = [
                    pool.apply_async(worker, args=(chunk, cropped_list_),
                                     callback=lambda _: pbar.update(1)) for chunk in chunk_group
                ]

                # Işçi sonuçlarını listede toplamak için
                # '+=' olması gerektiğini farketmem uzun sürdü, çok.
                chunk_results += [result.get() for result in results_list]

            except Exception as e:
                print(f"An error occurred in multiprocessing in main function: {e}")
                raise SystemExit

    pbar.close()  # Tamamlanan ProgressBar'ı Kapat.
    finish_time = time.time()  # Paralel olarak Toplam çalışma süresi
    ex_time = time.time()  # Saving işlem süresini başlat.
    save_prime_list(chunk_results)  # Hesaplanan asalları kaydet
    details_of_stored_pkl_below()  # Kaydedilen son dosya hakkında Bilgi ver.
    xe_time = time.time()  # Saving işlem süresini bitir.

    # Tamamlanma sürelerini terminalde yazdır.
    print(f"\033[1mTotal Calc. Time of Multiprocessing: {finish_time - start_time} second(s) / "
          f"{(finish_time - start_time) / 60} minute\033[1n")
    print(f"\033[1mTotal Calc. Time of Program: {finish_time + xe_time - start_time - ex_time} second(s) / "
          f"{(finish_time + xe_time - start_time - ex_time) / 60} minute\033[1n")

    kill_the_program()


def kill_the_program():
    # Programı başarılı sonlandır.
    print("Processing completed successfully.")
    print("\033[1m WabaLabaDubDub \033[0m")
    print("\033[1m:) boom\033[1n")
    sys.exit(0)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    start_program()
    main()
