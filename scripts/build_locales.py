from pathlib import Path
import re
import subprocess


MSGIDS = [
    "current passcode",
    "new passcode",
    "confirm passcode",
    "incorrect current passcode",
    "passcodes do not match",
    "e.g. spotify",
    "leave blank to keep existing passcode",
    "superadmin only",
    "budget updated.",
    "Finance Tracker",
    "Dashboard",
    "Transactions",
    "Analytics",
    "Recurring",
    "Settings",
    "operator",
    "Change Passcode",
    "Disconnect",
    "developed by",
    "reset passcode",
    "close",
    "// enter your email. we'll send a 6-digit verification code.",
    "email",
    "Cancel",
    "Send Code",
    "change passcode",
    "confirm new passcode",
    "// forgot your passcode?",
    "Save",
    "auth",
    "tracker",
    "language",
    "identify yourself",
    "access denied. invalid credentials.",
    "operator id",
    "passcode",
    "keep me logged in",
    "Authenticate",
    "MonEx",
    "analytics / patterns",
    "// pattern scan",
    "flow diagnostics",
    "Total Expenses",
    "outflow this cycle",
    "Total Income",
    "inflow this cycle",
    "Avg / Day",
    "daily burn rate",
    "Entries",
    "events logged",
    "Recurring Queue",
    "payments left this cycle",
    "current cycle only",
    "amount left",
    "all clear",
    "no live queue",
    "savings rate",
    "of income retained",
    "weekly spend",
    "category evolution",
    "this vs last month",
    "category comparison",
    "category movers",
    "vs last month",
    "spending velocity",
    "cumulative vs projected",
    "12-month flow",
    "income vs expense",
    "top spending days",
    "no spending days",
    "payment queue",
    "remaining this cycle",
    "day",
    "total",
    "all recurring payments cleared",
    "no live payment queue for this cycle",
    "largest outflows",
    "selected cycle",
    "name",
    "category",
    "date",
    "amount",
    "no expense outflows this cycle",
    "home",
    "toggle menu",
    "dashboard",
    "dashboard / overview",
    "// system online",
    "cycle",
    "over budget — %(pct)s%% of %(symbol)s%(amount)s cap consumed",
    "monthly cap",
    "// overspent by %(symbol)s%(spent)s − %(symbol)s%(cap)s = ",
    "// %(symbol)s%(remaining)s remaining in cycle",
    "no spend cap set for this cycle",
    "configure budget",
    "Income",
    "credits in",
    "Expense",
    "debits out",
    "Net",
    "balance delta",
    "events this cycle",
    "expenses by category",
    "bank movement",
    "recurring / scheduled",
    "// recurring queue",
    "scheduled flow",
    "New Rule",
    "To Pay",
    "paid %(symbol)s%(amount)s so far",
    "To Receive",
    "received %(symbol)s%(amount)s so far",
    "Net Remaining",
    "income − expense (pending)",
    "Payments Left",
    "pending recurring expenses",
    "Name",
    "Kind",
    "Day",
    "Bank",
    "Category",
    "Amount",
    "received",
    "pending",
    "paid",
    "pay",
    "paused",
    "edit",
    "no recurring rules",
    "settings / config",
    "Budget",
    "Banks",
    "Categories",
    "Users",
    "currency",
    "overall monthly cap",
    "cap",
    "leave empty for no cap",
    "Save Budget",
    "// when expenses exceed this, the dashboard goes red.",
    "per-category caps",
    "Cap",
    "New Bank",
    "New Category",
    "New Operator",
    "transactions / ledger",
    "// transaction ledger",
    "Add",
    "Date",
    "no entries logged",
    "no transactions for %(selected_month)s",
    "e.g. groceries lidl",
]

PLURAL_FORMS = {
    "es": "nplurals=2; plural=(n != 1);",
    "pt": "nplurals=2; plural=(n != 1);",
    "pl": "nplurals=4; plural=(n==1 ? 0 : (n%10>=2 && n%10<=4) && (n%100<12 || n%100>14) ? 1 : n!=1 && (n%10>=0 && n%10<=1) || (n%10>=5 && n%10<=9) || (n%100>=12 && n%100<=14) ? 2 : 3);",
    "fr": "nplurals=2; plural=(n > 1);",
    "de": "nplurals=2; plural=(n != 1);",
    "it": "nplurals=2; plural=(n != 1);",
    "ro": "nplurals=3; plural=(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2);",
    "ru": "nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : 2);",
    "ja": "nplurals=1; plural=0;",
    "ko": "nplurals=1; plural=0;",
    "zh-hans": "nplurals=1; plural=0;",
    "zh-hant": "nplurals=1; plural=0;",
    "ar": "nplurals=6; plural=n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 && n%100<=99 ? 4 : 5;",
}

LOCALE_DIRS = {
    "zh-hans": "zh_Hans",
    "zh-hant": "zh_Hant",
}

PATCH_EXISTING = {
    "es": {
        "confirm passcode": "confirmar código",
        "MonEx": "MonEx",
        "home": "inicio",
        "over budget — %(pct)s%% of %(symbol)s%(amount)s cap consumed": "sobrepresupuesto — %(pct)s%% del tope de %(symbol)s%(amount)s consumido",
        "// overspent by %(symbol)s%(spent)s − %(symbol)s%(cap)s = ": "// excedido por %(symbol)s%(spent)s − %(symbol)s%(cap)s = ",
        "// %(symbol)s%(remaining)s remaining in cycle": "// %(symbol)s%(remaining)s restantes en el ciclo",
        "paid %(symbol)s%(amount)s so far": "pagado %(symbol)s%(amount)s hasta ahora",
        "received %(symbol)s%(amount)s so far": "recibido %(symbol)s%(amount)s hasta ahora",
        "e.g. groceries lidl": "p. ej. compras lidl",
    },
    "pt": {
        "confirm passcode": "confirmar código",
        "MonEx": "MonEx",
        "home": "início",
        "over budget — %(pct)s%% of %(symbol)s%(amount)s cap consumed": "acima do orçamento — %(pct)s%% do teto de %(symbol)s%(amount)s consumido",
        "// overspent by %(symbol)s%(spent)s − %(symbol)s%(cap)s = ": "// excedido em %(symbol)s%(spent)s − %(symbol)s%(cap)s = ",
        "// %(symbol)s%(remaining)s remaining in cycle": "// %(symbol)s%(remaining)s em falta neste ciclo",
        "paid %(symbol)s%(amount)s so far": "pago %(symbol)s%(amount)s até agora",
        "received %(symbol)s%(amount)s so far": "recebido %(symbol)s%(amount)s até agora",
        "e.g. groceries lidl": "ex. compras lidl",
    },
    "pl": {
        "confirm passcode": "potwierdź kod",
        "MonEx": "MonEx",
        "home": "start",
        "over budget — %(pct)s%% of %(symbol)s%(amount)s cap consumed": "ponad budżet — wykorzystano %(pct)s%% limitu %(symbol)s%(amount)s",
        "// overspent by %(symbol)s%(spent)s − %(symbol)s%(cap)s = ": "// przekroczono o %(symbol)s%(spent)s − %(symbol)s%(cap)s = ",
        "// %(symbol)s%(remaining)s remaining in cycle": "// %(symbol)s%(remaining)s pozostało w cyklu",
        "paid %(symbol)s%(amount)s so far": "opłacono %(symbol)s%(amount)s do tej pory",
        "received %(symbol)s%(amount)s so far": "otrzymano %(symbol)s%(amount)s do tej pory",
        "e.g. groceries lidl": "np. zakupy lidl",
    },
}

RAW_TRANSLATIONS = {
    "fr": """
code actuel
nouveau code
confirmer le code
code actuel incorrect
les codes ne correspondent pas
ex. spotify
laissez vide pour conserver le code actuel
superadmin uniquement
budget mis à jour.
Suivi Financier
Tableau de bord
Transactions
Analytique
Récurrent
Paramètres
opérateur
Changer le code
Déconnecter
développé par
réinitialiser le code
fermer
// saisissez votre e-mail. nous enverrons un code de vérification à 6 chiffres.
e-mail
Annuler
Envoyer le code
changer le code
confirmer le nouveau code
// code oublié ?
Enregistrer
auth
suivi
langue
identifiez-vous
accès refusé. identifiants invalides.
identifiant opérateur
code
rester connecté
Authentifier
MonEx
analytique / tendances
// analyse des motifs
diagnostic des flux
Dépenses totales
sorties de ce cycle
Revenus totaux
entrées de ce cycle
Moy. / Jour
rythme de dépense quotidien
Entrées
événements enregistrés
File récurrente
paiements restants ce cycle
cycle en cours uniquement
montant restant
tout est réglé
aucune file active
taux d'épargne
du revenu conservé
dépense hebdomadaire
évolution des catégories
ce mois vs mois dernier
comparaison des catégories
catégories en mouvement
vs mois dernier
vitesse de dépense
cumulé vs projeté
flux sur 12 mois
revenus vs dépenses
jours les plus dépensiers
aucun jour de dépense
file de paiements
restant ce cycle
jour
total
tous les paiements récurrents sont réglés
aucune file de paiement active pour ce cycle
plus grosses sorties
cycle sélectionné
nom
catégorie
date
montant
aucune sortie de dépense ce cycle
accueil
ouvrir le menu
tableau de bord
tableau de bord / vue d'ensemble
// système en ligne
cycle
dépassement — %(pct)s%% du plafond de %(symbol)s%(amount)s consommé
plafond mensuel
// dépassé de %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// %(symbol)s%(remaining)s restants dans ce cycle
aucun plafond de dépense défini pour ce cycle
configurer le budget
Revenu
crédits entrants
Dépense
débits sortants
Net
delta du solde
événements de ce cycle
dépenses par catégorie
mouvement bancaire
récurrent / planifié
// file récurrente
flux planifié
Nouvelle règle
À payer
%(symbol)s%(amount)s payés jusqu'ici
À recevoir
%(symbol)s%(amount)s reçus jusqu'ici
Net restant
revenu − dépense (en attente)
Paiements restants
dépenses récurrentes en attente
Nom
Type
Jour
Banque
Catégorie
Montant
reçu
en attente
payé
payer
en pause
modifier
aucune règle récurrente
paramètres / config
Budget
Banques
Catégories
Utilisateurs
devise
plafond mensuel global
plafond
laissez vide pour aucun plafond
Enregistrer le budget
// lorsque les dépenses dépassent ce seuil, le tableau de bord passe au rouge.
plafonds par catégorie
Plafond
Nouvelle banque
Nouvelle catégorie
Nouvel opérateur
transactions / registre
// registre des transactions
Ajouter
Date
aucune entrée enregistrée
aucune transaction pour %(selected_month)s
ex. courses lidl
""",
    "de": """
aktueller Code
neuer Code
Code bestätigen
aktueller Code ist falsch
Codes stimmen nicht überein
z. B. spotify
leer lassen, um den bestehenden Code zu behalten
nur Superadmin
Budget aktualisiert.
Finanz-Tracker
Dashboard
Transaktionen
Analysen
Wiederkehrend
Einstellungen
Operator
Code ändern
Trennen
entwickelt von
Code zurücksetzen
schließen
// gib deine E-Mail ein. wir senden einen 6-stelligen Bestätigungscode.
E-Mail
Abbrechen
Code senden
Code ändern
neuen Code bestätigen
// Code vergessen?
Speichern
auth
tracker
Sprache
identifiziere dich
zugriff verweigert. ungültige anmeldedaten.
Operator-ID
Code
angemeldet bleiben
Authentifizieren
MonEx
analysen / muster
// musterscan
flussdiagnostik
Gesamtausgaben
Ausfluss in diesem Zyklus
Gesamteinnahmen
Zufluss in diesem Zyklus
Ø / Tag
tägliche Ausgaberate
Einträge
erfasste Ereignisse
Wiederkehrende Warteschlange
verbleibende Zahlungen in diesem Zyklus
nur aktueller Zyklus
verbleibender Betrag
alles erledigt
keine aktive Warteschlange
Sparquote
vom Einkommen behalten
wöchentliche Ausgaben
Kategorieentwicklung
dieser Monat vs letzter Monat
Kategorievergleich
Kategoriebewegungen
vs letzter Monat
Ausgabegeschwindigkeit
kumuliert vs prognostiziert
12-Monats-Fluss
Einnahmen vs Ausgaben
Tage mit höchsten Ausgaben
keine Ausgabetage
Zahlungswarteschlange
verbleibend in diesem Zyklus
Tag
gesamt
alle wiederkehrenden Zahlungen erledigt
keine aktive Zahlungswarteschlange für diesen Zyklus
größte Abflüsse
ausgewählter Zyklus
Name
Kategorie
Datum
Betrag
keine Ausgabenabflüsse in diesem Zyklus
Startseite
Menü umschalten
dashboard
dashboard / übersicht
// system online
zyklus
über Budget — %(pct)s%% von %(symbol)s%(amount)s des Limits verbraucht
Monatslimit
// überzogen um %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// %(symbol)s%(remaining)s verbleiben in diesem Zyklus
kein Ausgabelimit für diesen Zyklus festgelegt
Budget konfigurieren
Einnahmen
Gutschriften rein
Ausgaben
Abbuchungen raus
Netto
Saldoänderung
Ereignisse in diesem Zyklus
Ausgaben nach Kategorie
Bankbewegung
wiederkehrend / geplant
// wiederkehrende Warteschlange
geplanter Fluss
Neue Regel
Zu zahlen
%(symbol)s%(amount)s bisher bezahlt
Zu erhalten
%(symbol)s%(amount)s bisher erhalten
Verbleibendes Netto
Einnahmen − Ausgaben (ausstehend)
Verbleibende Zahlungen
ausstehende wiederkehrende Ausgaben
Name
Art
Tag
Bank
Kategorie
Betrag
erhalten
ausstehend
bezahlt
zahlen
pausiert
bearbeiten
keine wiederkehrenden Regeln
einstellungen / konfiguration
Budget
Banken
Kategorien
Benutzer
Währung
gesamtmonatliches Limit
Limit
leer lassen für kein Limit
Budget speichern
// wenn Ausgaben diesen Wert überschreiten, wird das Dashboard rot.
Limits pro Kategorie
Limit
Neue Bank
Neue Kategorie
Neuer Operator
transaktionen / buch
// transaktionsbuch
Hinzufügen
Datum
keine Einträge erfasst
keine Transaktionen für %(selected_month)s
z. B. lebensmittel lidl
""",
    "it": """
codice attuale
nuovo codice
conferma codice
codice attuale errato
i codici non corrispondono
es. spotify
lascia vuoto per mantenere il codice attuale
solo superadmin
budget aggiornato.
Tracker Finanziario
Dashboard
Transazioni
Analisi
Ricorrenti
Impostazioni
operatore
Cambia codice
Disconnetti
sviluppato da
reimposta codice
chiudi
// inserisci la tua email. invieremo un codice di verifica di 6 cifre.
email
Annulla
Invia codice
cambia codice
conferma nuovo codice
// hai dimenticato il codice?
Salva
auth
tracker
lingua
identificati
accesso negato. credenziali non valide.
id operatore
codice
resta connesso
Autentica
MonEx
analisi / pattern
// scansione pattern
diagnostica del flusso
Spese totali
uscite in questo ciclo
Entrate totali
entrate in questo ciclo
Media / Giorno
ritmo di spesa giornaliero
Voci
eventi registrati
Coda ricorrente
pagamenti rimasti in questo ciclo
solo ciclo corrente
importo rimanente
tutto a posto
nessuna coda attiva
tasso di risparmio
del reddito trattenuto
spesa settimanale
evoluzione categorie
questo mese vs mese scorso
confronto categorie
variazioni categorie
vs mese scorso
velocità di spesa
cumulato vs previsto
flusso a 12 mesi
entrate vs spese
giorni di spesa principali
nessun giorno di spesa
coda pagamenti
rimanente in questo ciclo
giorno
totale
tutti i pagamenti ricorrenti sono completati
nessuna coda pagamenti attiva per questo ciclo
maggiori uscite
ciclo selezionato
nome
categoria
data
importo
nessuna uscita di spesa in questo ciclo
home
apri menu
dashboard
dashboard / panoramica
// sistema online
ciclo
fuori budget — %(pct)s%% del tetto di %(symbol)s%(amount)s consumato
tetto mensile
// sforato di %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// %(symbol)s%(remaining)s rimanenti nel ciclo
nessun limite di spesa impostato per questo ciclo
configura budget
Entrate
accrediti in entrata
Spesa
addebiti in uscita
Netto
delta saldo
eventi in questo ciclo
spese per categoria
movimento bancario
ricorrenti / pianificati
// coda ricorrente
flusso pianificato
Nuova regola
Da pagare
pagati %(symbol)s%(amount)s finora
Da ricevere
ricevuti %(symbol)s%(amount)s finora
Netto rimanente
entrate − spese (in sospeso)
Pagamenti rimasti
spese ricorrenti in sospeso
Nome
Tipo
Giorno
Banca
Categoria
Importo
ricevuto
in sospeso
pagato
paga
in pausa
modifica
nessuna regola ricorrente
impostazioni / config
Budget
Banche
Categorie
Utenti
valuta
tetto mensile complessivo
tetto
lascia vuoto per nessun tetto
Salva budget
// quando le spese superano questa soglia, la dashboard diventa rossa.
tetti per categoria
Tetto
Nuova banca
Nuova categoria
Nuovo operatore
transazioni / registro
// registro transazioni
Aggiungi
Data
nessuna voce registrata
nessuna transazione per %(selected_month)s
es. spesa lidl
""",
    "ro": """
cod actual
cod nou
confirmă codul
codul actual este incorect
codurile nu se potrivesc
ex. spotify
lasă gol pentru a păstra codul existent
doar superadmin
buget actualizat.
Tracker Financiar
Tablou de bord
Tranzacții
Analitice
Recurente
Setări
operator
Schimbă codul
Deconectează
dezvoltat de
resetează codul
închide
// introdu emailul. vom trimite un cod de verificare din 6 cifre.
email
Anulează
Trimite codul
schimbă codul
confirmă noul cod
// ai uitat codul?
Salvează
auth
tracker
limbă
identifică-te
acces refuzat. credențiale invalide.
id operator
cod
păstrează-mă autentificat
Autentifică
MonEx
analitice / modele
// scanare modele
diagnostic flux
Cheltuieli totale
ieșiri în acest ciclu
Venit total
intrări în acest ciclu
Medie / Zi
ritm zilnic de cheltuire
Intrări
evenimente înregistrate
Coadă recurentă
plăți rămase în acest ciclu
doar ciclul curent
sumă rămasă
totul este în regulă
fără coadă activă
rată de economisire
din venit păstrat
cheltuială săptămânală
evoluția categoriilor
luna aceasta vs luna trecută
comparație categorii
mișcări pe categorii
vs luna trecută
viteza cheltuielilor
cumulat vs proiectat
flux pe 12 luni
venit vs cheltuială
zilele cu cele mai mari cheltuieli
fără zile de cheltuieli
coadă de plăți
rămas în acest ciclu
zi
total
toate plățile recurente sunt achitate
nu există coadă activă de plăți pentru acest ciclu
cele mai mari ieșiri
ciclul selectat
nume
categorie
dată
sumă
fără ieșiri de cheltuieli în acest ciclu
acasă
comută meniul
tablou de bord
tablou de bord / prezentare
// sistem online
ciclu
peste buget — %(pct)s%% din plafonul de %(symbol)s%(amount)s consumat
plafon lunar
// depășit cu %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// %(symbol)s%(remaining)s rămași în acest ciclu
nu există plafon de cheltuieli setat pentru acest ciclu
configurează bugetul
Venit
credite intrate
Cheltuială
debite ieșite
Net
diferență sold
evenimente în acest ciclu
cheltuieli pe categorii
mișcare bancară
recurente / programate
// coadă recurentă
flux programat
Regulă nouă
De plătit
plătit %(symbol)s%(amount)s până acum
De primit
primit %(symbol)s%(amount)s până acum
Net rămas
venit − cheltuială (în așteptare)
Plăți rămase
cheltuieli recurente în așteptare
Nume
Tip
Zi
Bancă
Categorie
Sumă
primit
în așteptare
plătit
plătește
pus pe pauză
editează
fără reguli recurente
setări / config
Buget
Bănci
Categorii
Utilizatori
monedă
plafon lunar general
plafon
lasă gol pentru fără plafon
Salvează bugetul
// când cheltuielile depășesc acest prag, tabloul de bord devine roșu.
plafoane pe categorii
Plafon
Bancă nouă
Categorie nouă
Operator nou
tranzacții / registru
// registru tranzacții
Adaugă
Dată
nu există intrări înregistrate
nu există tranzacții pentru %(selected_month)s
ex. cumpărături lidl
""",
    "ru": """
текущий код
новый код
подтвердите код
неверный текущий код
коды не совпадают
напр. spotify
оставьте пустым, чтобы сохранить текущий код
только для суперадмина
бюджет обновлен.
Финансовый трекер
Панель
Транзакции
Аналитика
Регулярные
Настройки
оператор
Сменить код
Отключиться
разработано
сбросить код
закрыть
// введите email. мы отправим 6-значный код подтверждения.
email
Отмена
Отправить код
сменить код
подтвердите новый код
// забыли код?
Сохранить
auth
трекер
язык
идентифицируйтесь
доступ запрещен. неверные учетные данные.
id оператора
код
оставаться в системе
Авторизоваться
MonEx
аналитика / паттерны
// сканирование паттернов
диагностика потока
Общие расходы
отток в этом цикле
Общий доход
приток в этом цикле
Средн. / День
дневная скорость трат
Записи
события записаны
Очередь регулярных
платежей осталось в этом цикле
только текущий цикл
осталось суммы
все чисто
нет активной очереди
норма сбережений
сохранено от дохода
расходы по неделям
эволюция категорий
этот месяц vs прошлый месяц
сравнение категорий
движение категорий
vs прошлый месяц
скорость расходов
накопленное vs прогноз
поток за 12 месяцев
доход vs расход
дни с наибольшими расходами
нет дней с расходами
очередь платежей
осталось в этом цикле
день
итого
все регулярные платежи закрыты
нет активной очереди платежей для этого цикла
крупнейшие оттоки
выбранный цикл
название
категория
дата
сумма
в этом цикле нет расходных оттоков
главная
переключить меню
панель
панель / обзор
// система онлайн
цикл
сверх бюджета — использовано %(pct)s%% лимита %(symbol)s%(amount)s
месячный лимит
// перерасход на %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// %(symbol)s%(remaining)s осталось в цикле
для этого цикла не задан лимит расходов
настроить бюджет
Доход
поступления
Расход
списания
Итог
изменение баланса
события в этом цикле
расходы по категориям
движение по банкам
регулярные / по расписанию
// очередь регулярных
плановый поток
Новое правило
К оплате
оплачено %(symbol)s%(amount)s на данный момент
К получению
получено %(symbol)s%(amount)s на данный момент
Остаток нетто
доход − расход (в ожидании)
Осталось платежей
ожидающие регулярные расходы
Название
Тип
День
Банк
Категория
Сумма
получено
в ожидании
оплачено
оплатить
на паузе
редактировать
нет регулярных правил
настройки / конфиг
Бюджет
Банки
Категории
Пользователи
валюта
общий месячный лимит
лимит
оставьте пустым для отсутствия лимита
Сохранить бюджет
// когда расходы превышают этот порог, панель становится красной.
лимиты по категориям
Лимит
Новый банк
Новая категория
Новый оператор
транзакции / журнал
// журнал транзакций
Добавить
Дата
нет записей
нет транзакций за %(selected_month)s
напр. покупки lidl
""",
    "ja": """
現在のパスコード
新しいパスコード
パスコードを確認
現在のパスコードが正しくありません
パスコードが一致しません
例: spotify
現在のパスコードを維持するには空欄のままにしてください
superadmin のみ
予算を更新しました。
ファイナンストラッカー
ダッシュボード
取引
分析
定期
設定
オペレーター
パスコードを変更
切断
開発者
パスコードをリセット
閉じる
// メールアドレスを入力してください。6桁の確認コードを送信します。
メール
キャンセル
コードを送信
パスコードを変更
新しいパスコードを確認
// パスコードを忘れましたか？
保存
認証
トラッカー
言語
本人確認してください
アクセス拒否。認証情報が無効です。
オペレーターID
パスコード
ログイン状態を保持
認証
MonEx
分析 / パターン
// パターンスキャン
フロー診断
総支出
このサイクルの流出
総収入
このサイクルの流入
平均 / 日
1日あたりの消費ペース
件数
記録されたイベント
定期キュー
このサイクルで残っている支払い
現在のサイクルのみ
残額
すべて完了
アクティブなキューはありません
貯蓄率
保持された収入の割合
週間支出
カテゴリ推移
今月 vs 先月
カテゴリ比較
カテゴリ変動
vs 先月
支出速度
累計 vs 予測
12か月フロー
収入 vs 支出
支出が多い日
支出日なし
支払いキュー
このサイクルの残り
日
合計
すべての定期支払いは完了しました
このサイクルにアクティブな支払いキューはありません
最大の流出
選択中のサイクル
名前
カテゴリ
日付
金額
このサイクルに支出の流出はありません
ホーム
メニュー切替
ダッシュボード
ダッシュボード / 概要
// システムオンライン
サイクル
予算超過 — 上限 %(symbol)s%(amount)s の %(pct)s%% を消費
月間上限
// 超過額 %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// このサイクルの残り %(symbol)s%(remaining)s
このサイクルには支出上限が設定されていません
予算を設定
収入
入金
支出
出金
純額
残高差分
このサイクルのイベント
カテゴリ別支出
銀行の動き
定期 / 予定
// 定期キュー
予定フロー
新しいルール
支払予定
これまでに %(symbol)s%(amount)s 支払い済み
受取予定
これまでに %(symbol)s%(amount)s 受取済み
残り純額
収入 − 支出（保留中）
残り支払い
保留中の定期支出
名前
種別
日
銀行
カテゴリ
金額
受取済み
保留中
支払済み
支払う
一時停止
編集
定期ルールはありません
設定 / 構成
予算
銀行
カテゴリ
ユーザー
通貨
全体の月間上限
上限
上限なしにするには空欄
予算を保存
// 支出がこの値を超えると、ダッシュボードは赤になります。
カテゴリごとの上限
上限
新しい銀行
新しいカテゴリ
新しいオペレーター
取引 / 台帳
// 取引台帳
追加
日付
記録された項目はありません
%(selected_month)s の取引はありません
例: lidl の食料品
""",
    "ko": """
현재 패스코드
새 패스코드
패스코드 확인
현재 패스코드가 올바르지 않습니다
패스코드가 일치하지 않습니다
예: spotify
기존 패스코드를 유지하려면 비워 두세요
슈퍼관리자 전용
예산이 업데이트되었습니다.
재무 추적기
대시보드
거래
분석
반복
설정
운영자
패스코드 변경
연결 해제
개발
패스코드 재설정
닫기
// 이메일을 입력하세요. 6자리 확인 코드를 보냅니다.
이메일
취소
코드 보내기
패스코드 변경
새 패스코드 확인
// 패스코드를 잊으셨나요?
저장
인증
추적기
언어
본인 확인
접근이 거부되었습니다. 자격 증명이 올바르지 않습니다.
운영자 ID
패스코드
로그인 상태 유지
인증
MonEx
분석 / 패턴
// 패턴 스캔
흐름 진단
총 지출
이 사이클의 유출
총 수입
이 사이클의 유입
평균 / 일
일일 소진 속도
항목 수
기록된 이벤트
반복 큐
이 사이클에 남은 결제
현재 사이클만
남은 금액
모두 완료
활성 큐 없음
저축률
유지된 수입 비율
주간 지출
카테고리 변화
이번 달 vs 지난달
카테고리 비교
카테고리 변동
vs 지난달
지출 속도
누적 vs 예상
12개월 흐름
수입 vs 지출
지출이 큰 날
지출한 날 없음
결제 큐
이 사이클의 남은 항목
일
총계
모든 반복 결제가 완료되었습니다
이 사이클에 활성 결제 큐가 없습니다
가장 큰 유출
선택한 사이클
이름
카테고리
날짜
금액
이 사이클에는 지출 유출이 없습니다
홈
메뉴 전환
대시보드
대시보드 / 개요
// 시스템 온라인
사이클
예산 초과 — 한도 %(symbol)s%(amount)s 의 %(pct)s%% 사용됨
월간 한도
// 초과 금액 %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// 이 사이클에 %(symbol)s%(remaining)s 남음
이 사이클에는 지출 한도가 설정되지 않았습니다
예산 설정
수입
입금
지출
출금
순액
잔액 변화
이 사이클의 이벤트
카테고리별 지출
은행 움직임
반복 / 예약
// 반복 큐
예정 흐름
새 규칙
결제 예정
지금까지 %(symbol)s%(amount)s 결제됨
수령 예정
지금까지 %(symbol)s%(amount)s 수령됨
남은 순액
수입 − 지출(대기 중)
남은 결제
대기 중인 반복 지출
이름
종류
일
은행
카테고리
금액
수령됨
대기 중
결제됨
결제
일시중지
수정
반복 규칙이 없습니다
설정 / 구성
예산
은행
카테고리
사용자
통화
전체 월간 한도
한도
한도 없으면 비워 두세요
예산 저장
// 지출이 이 값을 넘으면 대시보드가 빨간색으로 바뀝니다.
카테고리별 한도
한도
새 은행
새 카테고리
새 운영자
거래 / 원장
// 거래 원장
추가
날짜
기록된 항목이 없습니다
%(selected_month)s 에 대한 거래가 없습니다
예: lidl 식료품
""",
    "zh-hans": """
当前密码
新密码
确认密码
当前密码不正确
密码不匹配
例如：spotify
留空以保留现有密码
仅限超级管理员
预算已更新。
财务追踪器
仪表盘
交易
分析
周期项目
设置
操作员
更改密码
断开连接
开发者
重置密码
关闭
// 输入你的邮箱。我们会发送一个 6 位验证码。
邮箱
取消
发送验证码
更改密码
确认新密码
// 忘记密码？
保存
认证
追踪器
语言
请进行身份验证
访问被拒绝。凭据无效。
操作员 ID
密码
保持登录
认证
MonEx
分析 / 模式
// 模式扫描
流向诊断
总支出
本周期流出
总收入
本周期流入
日均
每日支出速率
条目
已记录事件
周期队列
本周期剩余付款
仅当前周期
剩余金额
已全部完成
没有活动队列
储蓄率
保留收入占比
每周支出
类别演变
本月 vs 上月
类别对比
类别变动
vs 上月
支出速度
累计 vs 预测
12 个月流向
收入 vs 支出
支出最高日期
没有支出日期
付款队列
本周期剩余
天
总计
所有周期付款已结清
本周期没有活动付款队列
最大流出
所选周期
名称
类别
日期
金额
本周期没有支出流出
首页
切换菜单
仪表盘
仪表盘 / 概览
// 系统在线
周期
超出预算 — 已消耗 %(symbol)s%(amount)s 上限的 %(pct)s%%
月度上限
// 超支 %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// 本周期剩余 %(symbol)s%(remaining)s
本周期未设置支出上限
配置预算
收入
收入流入
支出
支出流出
净额
余额变化
本周期事件
按类别支出
银行变动
周期 / 计划
// 周期队列
计划流向
新规则
待支付
目前已支付 %(symbol)s%(amount)s
待收取
目前已收取 %(symbol)s%(amount)s
剩余净额
收入 − 支出（待处理）
剩余付款
待处理的周期支出
名称
类型
日
银行
类别
金额
已收取
待处理
已支付
支付
已暂停
编辑
没有周期规则
设置 / 配置
预算
银行
类别
用户
货币
整体月度上限
上限
留空表示无上限
保存预算
// 当支出超过此值时，仪表盘会变红。
分类上限
上限
新银行
新类别
新操作员
交易 / 台账
// 交易台账
添加
日期
没有已记录条目
%(selected_month)s 没有交易
例如：lidl 杂货
""",
    "zh-hant": """
目前密碼
新密碼
確認密碼
目前密碼不正確
密碼不相符
例如：spotify
留白以保留現有密碼
僅限超級管理員
預算已更新。
財務追蹤器
儀表板
交易
分析
週期項目
設定
操作員
變更密碼
中斷連線
開發者
重設密碼
關閉
// 輸入你的電子郵件。我們會送出 6 位數驗證碼。
電子郵件
取消
傳送驗證碼
變更密碼
確認新密碼
// 忘記密碼？
儲存
驗證
追蹤器
語言
請先驗證身分
存取遭拒。憑證無效。
操作員 ID
密碼
保持登入
驗證
MonEx
分析 / 模式
// 模式掃描
流向診斷
總支出
本週期流出
總收入
本週期流入
平均 / 日
每日支出速率
項目
已記錄事件
週期佇列
本週期剩餘付款
僅目前週期
剩餘金額
全部完成
沒有作用中的佇列
儲蓄率
保留下來的收入比例
每週支出
類別演變
本月 vs 上月
類別比較
類別變動
vs 上月
支出速度
累積 vs 預估
12 個月流向
收入 vs 支出
支出最高的日子
沒有支出日
付款佇列
本週期剩餘
日
總計
所有週期付款都已結清
本週期沒有作用中的付款佇列
最大流出
所選週期
名稱
類別
日期
金額
本週期沒有支出流出
首頁
切換選單
儀表板
儀表板 / 概覽
// 系統上線
週期
超出預算 — 已消耗 %(symbol)s%(amount)s 上限的 %(pct)s%%
每月上限
// 超支 %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// 本週期剩餘 %(symbol)s%(remaining)s
此週期未設定支出上限
設定預算
收入
收入流入
支出
支出流出
淨額
餘額變化
本週期事件
按類別支出
銀行變動
週期 / 排程
// 週期佇列
排程流向
新規則
待付款
目前已支付 %(symbol)s%(amount)s
待收款
目前已收取 %(symbol)s%(amount)s
剩餘淨額
收入 − 支出（待處理）
剩餘付款
待處理的週期支出
名稱
類型
日
銀行
類別
金額
已收取
待處理
已支付
支付
已暫停
編輯
沒有週期規則
設定 / 配置
預算
銀行
類別
使用者
貨幣
整體每月上限
上限
留白表示無上限
儲存預算
// 當支出超過這個值時，儀表板會變成紅色。
各類別上限
上限
新銀行
新類別
新操作員
交易 / 台帳
// 交易台帳
新增
日期
沒有已記錄項目
%(selected_month)s 沒有交易
例如：lidl 雜貨
""",
    "ar": """
رمز المرور الحالي
رمز مرور جديد
تأكيد رمز المرور
رمز المرور الحالي غير صحيح
رموز المرور غير متطابقة
مثال: spotify
اتركه فارغًا للاحتفاظ برمز المرور الحالي
للمشرف الأعلى فقط
تم تحديث الميزانية.
متعقب مالي
لوحة التحكم
المعاملات
التحليلات
المتكرر
الإعدادات
المشغل
تغيير رمز المرور
قطع الاتصال
تم التطوير بواسطة
إعادة تعيين رمز المرور
إغلاق
// أدخل بريدك الإلكتروني. سنرسل رمز تحقق مكوّنًا من 6 أرقام.
البريد الإلكتروني
إلغاء
إرسال الرمز
تغيير رمز المرور
تأكيد رمز المرور الجديد
// هل نسيت رمز المرور؟
حفظ
المصادقة
المتعقب
اللغة
عرّف نفسك
تم رفض الوصول. بيانات الاعتماد غير صالحة.
معرّف المشغل
رمز المرور
أبقني مسجلاً
مصادقة
MonEx
التحليلات / الأنماط
// فحص الأنماط
تشخيص التدفق
إجمالي المصروفات
التدفق الخارج في هذه الدورة
إجمالي الدخل
التدفق الداخل في هذه الدورة
المتوسط / اليوم
معدل الحرق اليومي
المدخلات
الأحداث المسجلة
قائمة المتكرر
المدفوعات المتبقية في هذه الدورة
الدورة الحالية فقط
المبلغ المتبقي
تم كل شيء
لا توجد قائمة نشطة
معدل الادخار
من الدخل المحتفظ به
الإنفاق الأسبوعي
تطور الفئات
هذا الشهر مقابل الشهر الماضي
مقارنة الفئات
تحركات الفئات
مقابل الشهر الماضي
سرعة الإنفاق
التراكمي مقابل المتوقع
تدفق 12 شهرًا
الدخل مقابل المصروفات
أعلى أيام الإنفاق
لا توجد أيام إنفاق
قائمة المدفوعات
المتبقي في هذه الدورة
اليوم
الإجمالي
تمت تسوية كل المدفوعات المتكررة
لا توجد قائمة مدفوعات نشطة لهذه الدورة
أكبر التدفقات الخارجة
الدورة المحددة
الاسم
الفئة
التاريخ
المبلغ
لا توجد تدفقات خارجة للمصروفات في هذه الدورة
الرئيسية
تبديل القائمة
لوحة التحكم
لوحة التحكم / نظرة عامة
// النظام متصل
الدورة
فوق الميزانية — تم استهلاك %(pct)s%% من حد %(symbol)s%(amount)s
الحد الشهري
// تجاوز بمقدار %(symbol)s%(spent)s − %(symbol)s%(cap)s = 
// المتبقي %(symbol)s%(remaining)s في هذه الدورة
لا يوجد حد إنفاق مضبوط لهذه الدورة
ضبط الميزانية
الدخل
ائتمانات داخلة
المصروفات
خصومات خارجة
الصافي
تغير الرصيد
أحداث هذه الدورة
المصروفات حسب الفئة
حركة البنوك
متكرر / مجدول
// قائمة المتكرر
التدفق المجدول
قاعدة جديدة
للدفع
تم دفع %(symbol)s%(amount)s حتى الآن
للاستلام
تم استلام %(symbol)s%(amount)s حتى الآن
الصافي المتبقي
الدخل − المصروفات (قيد الانتظار)
المدفوعات المتبقية
مصروفات متكررة قيد الانتظار
الاسم
النوع
اليوم
البنك
الفئة
المبلغ
تم الاستلام
قيد الانتظار
تم الدفع
ادفع
متوقف
تعديل
لا توجد قواعد متكررة
الإعدادات / التهيئة
الميزانية
البنوك
الفئات
المستخدمون
العملة
الحد الشهري الإجمالي
الحد
اتركه فارغًا لعدم وجود حد
حفظ الميزانية
// عندما تتجاوز المصروفات هذه القيمة، تتحول لوحة التحكم إلى اللون الأحمر.
حدود حسب الفئة
الحد
بنك جديد
فئة جديدة
مشغل جديد
المعاملات / الدفتر
// دفتر المعاملات
إضافة
التاريخ
لا توجد مدخلات مسجلة
لا توجد معاملات في %(selected_month)s
مثال: بقالة lidl
""",
}


def parse_po(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    pairs = re.findall(r'^msgid "(.*)"\nmsgstr "(.*)"$', text, re.M)
    return {msgid: msgstr for msgid, msgstr in pairs if msgid}


def po_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def write_po(code: str, mapping: dict[str, str]) -> None:
    locale_name = LOCALE_DIRS.get(code, code)
    locale_dir = Path("locale") / locale_name / "LC_MESSAGES"
    locale_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        'msgid ""',
        'msgstr ""',
        '"Project-Id-Version: MonEx\\n"',
        f'"Language: {code}\\n"',
        '"MIME-Version: 1.0\\n"',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        f'"Plural-Forms: {PLURAL_FORMS[code]}\\n"',
        "",
    ]
    for msgid in MSGIDS:
        msgstr = mapping[msgid]
        lines.append(f'msgid "{po_escape(msgid)}"')
        lines.append(f'msgstr "{po_escape(msgstr)}"')
        lines.append("")
    po_path = locale_dir / "django.po"
    po_path.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run(["msgfmt", str(po_path), "-o", str(locale_dir / "django.mo")], check=True)


def build_existing(code: str) -> dict[str, str]:
    locale_name = LOCALE_DIRS.get(code, code)
    path = Path("locale") / locale_name / "LC_MESSAGES" / "django.po"
    mapping = parse_po(path)
    mapping.update(PATCH_EXISTING[code])
    missing = [msgid for msgid in MSGIDS if msgid not in mapping]
    if missing:
        raise SystemExit(f"{code} missing translations: {missing}")
    return {msgid: mapping[msgid] for msgid in MSGIDS}


def build_raw(code: str) -> dict[str, str]:
    values = RAW_TRANSLATIONS[code].strip("\n").splitlines()
    if len(values) != len(MSGIDS):
        raise SystemExit(f"{code} expected {len(MSGIDS)} translations, got {len(values)}")
    return dict(zip(MSGIDS, values, strict=True))


def main() -> None:
    for code in ("es", "pt", "pl"):
        write_po(code, build_existing(code))
    for code in ("fr", "de", "it", "ro", "ru", "ja", "ko", "zh-hans", "zh-hant", "ar"):
        write_po(code, build_raw(code))


if __name__ == "__main__":
    main()
