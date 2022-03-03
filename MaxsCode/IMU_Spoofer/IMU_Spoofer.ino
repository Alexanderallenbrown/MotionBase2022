
void setup() {
  // put your setup code here, to run once:
Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
Serial.print(random(10));
Serial.print("\t");
Serial.print(random(10));
Serial.print("\t");
Serial.print(random(10));
Serial.print("\t");
Serial.print(random(10));
Serial.print("\t");
Serial.print(random(10));
Serial.print("\t");
Serial.print(random(10));
Serial.print("\t");
Serial.print(millis()/1000.0);

Serial.println();

delay(10);
}
