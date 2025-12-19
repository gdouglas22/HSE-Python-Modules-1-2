import csv

def safe_int(v, default=0):
    try:
        if v is None:
            return default
        s = str(v).strip()
        if s == "":
            return default
        return int(float(s.replace(",", ".")))
    except:
        return default

class Client:
    def __init__(self, full_name, gender, age, device, browser, amount, region):
        self.full_name = (full_name or "").strip()
        self.gender = (gender or "").strip().lower()
        self.age = safe_int(age, 0)
        self.device = (device or "").strip().lower()
        self.browser = (browser or "").strip()
        self.amount = (str(amount).strip() if amount is not None else "0")
        self.region = (region or "").strip()

    def _gender_phrase(self):
        if self.gender in ("female", "женский", "женщина"):
            return "женского пола"
        elif self.gender in ("male", "мужской", "мужчина"):
            return "мужского пола"
        return "неопределённого пола"

    def _purchase_verb(self):
        if self.gender in ("female", "женский", "женщина"):
            return "совершила"
        elif self.gender in ("male", "мужской", "мужчина"):
            return "совершил"
        return "совершил(а)"

    def _age_word(self):
        n = self.age
        last_two = n % 100
        last = n % 10
        if 11 <= last_two <= 14:
            return "лет"
        if last == 1:
            return "год"
        if 2 <= last <= 4:
            return "года"
        return "лет"

    def _device_phrase(self):
        if self.device == "mobile":
            return "мобильного браузера"
        if self.device == "desktop":
            return "настольного браузера"
        if self.device == "tablet":
            return "планшетного браузера"
        return "браузера"

    def to_description(self):
        return (
            f"Пользователь {self.full_name} {self._gender_phrase()}, {self.age} {self._age_word()} "
            f"{self._purchase_verb()} покупку на {self.amount} у.е. с {self._device_phrase()} {self.browser}. "
            f"Регион, из которого совершалась покупка: {self.region}."
        )

def read_clients_from_csv(input_filename):
    clients = []
    with open(input_filename, "r", encoding="utf-8", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        reader = csv.DictReader(f, dialect=dialect)

        for row in reader:
            clients.append(Client(
                full_name=row.get("name", ""),
                gender=row.get("sex", ""),
                age=row.get("age", "0"),
                device=row.get("device_type", ""),
                browser=row.get("browser", ""),
                amount=row.get("bill", "0"),
                region=row.get("region", "")
            ))
    return clients

def write_descriptions_to_file(output_filename, descriptions):
    with open(output_filename, "w", encoding="utf-8") as f:
        for desc in descriptions:
            f.write(desc + "\n")

def generate_client_descriptions(input_filename, output_filename):
    clients = read_clients_from_csv(input_filename)
    descriptions = [c.to_description() for c in clients]
    write_descriptions_to_file(output_filename, descriptions)

if __name__ == "__main__":
    input_file = input("Введите имя входного файла: ")
    output_file = "descriptions.txt"
    generate_client_descriptions(input_file, output_file)
    print("Описания записаны в файл:", output_file)