#include <Wire.h>
#include <Sodaq_DS3231.h>

byte GetSeason() {
  const uint32_t SeasonTicks[4] = {8014464, 8091360, 7762176, 7688736}; // Sekunden pro Jahreszeit (Fruehling, Sommer, Herbst, Winter)
  uint32_t startdate = 1482320640; // als Startdatum fuer die Berechnung: 2016/12/21 11:44:00 Mittwoch = Winteranfang (UnixTime = 1482320640)
  byte SeasonCount = 3; // Winteranfang als Start
  DateTime now = rtc.now(); // das aktuelle Datum und die Uhrzeit aus der RTC lesen
  uint32_t unixtime = now.getEpoch(); // zum Vergleich die Unixzeit holen
  while (startdate + SeasonTicks[SeasonCount] < unixtime) { // Schleife solange durchlaufen, wie die Unixzeit nicht ueberschritten wird
    startdate += SeasonTicks[SeasonCount++]; // zum Startdatum die Sekunden pro Jahreszeit addieren und den Jahreszeiten-Zaehler erhoehen
    if (SeasonCount > 3) SeasonCount = 0;    // wenn der Jahreszeiten-Zaehler beim Winter (3) angekommen ist, wieder zum Fruehling (0) springen
  };
  return SeasonCount; // Jahreszeiten-Zaehler zurueckgeben
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  rtc.begin();
  DateTime dt(2017, 3, 20, 0, 0, 0, 0); // zum testen, das Datum verstellen
  rtc.setDateTime(dt);
  Serial.println(GetSeason()); // 0 = Fruehling, 1 = Sommer, 2 = Herbst, 3 = Winter
}

void loop() {

}
