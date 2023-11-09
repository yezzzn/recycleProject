//로봇팔 동작 코드

#include <Servo.h>

int currentindex=0;
int input[3];

const int SERVOS = 6;
int PIN[SERVOS];
Servo myservo[SERVOS];


int firstAngles[SERVOS] = {85, 50, 40, 20, 70, 0}; // 초기 각도 설정
int commands[6][SERVOS] = {
  {0, 80, 20, 30, 70, 0},
  {20, 80, 40, 20, 70, 0},
  {40, 100, 100, 60, 70, 0},
  {180, 80, 40, 20, 70, 0},
  {150, 80, 40, 20, 70, 0},
  {130, 100, 100, 60, 70, 0}
};
void setup() {
  PIN[0] = 2;
  PIN[1] = 3;
  PIN[2] = 9;
  PIN[3] = 8;
  PIN[4] = 4;
  PIN[5] = 5;

  for (int i = 0; i < SERVOS; i++) {
    myservo[i].attach(PIN[i]);
    myservo[i].write(firstAngles[i]); // 초기 각도로 설정
  }
  Serial.begin(9600);
}

void loop() {
  int hand1=0;
  int hand2=0;
  int hand3=0;
  
  if (Serial.available() > 0) {
    char a = Serial.read();
    if ( a >='1' && a<='6'){
      input[currentindex] = a - '1';
      currentindex++;  
      delay(100);
      if(currentindex ==3){
        // 동작수행
        delay(3000);
        for (int i = 85; i <= 105; i++){
        myservo[0].write(i); 
        delay(10);
      }
        for (int i = 60; i <= 130; i++){
        myservo[1].write(i); 
        delay(10);
      }
      delay(400);
      for (int i = 40; i <= 80; i++){
        myservo[2].write(i); 
        delay(10);
      }
      
      switch (input[0]) {
        case 0: //can
        case 3: //paper
        case 4: //plastic
        case 5: //label
            hand1 =50;
            break;
        case 2:  //glass
        case 1:
            hand1 = 60;
            break;
      }
      delay(1000);
      myservo[5].write(hand1);
      delay(500);
      
      for (int i = 120; i >= 60; i--){
        myservo[1].write(i); 
        delay(10);
      }
      delay(1000);
      for (int i = 0; i < SERVOS; i++) {
        int targetAngle = commands[input[0]][i];
        int currentAngle = myservo[i].read();
        int step = (targetAngle - currentAngle) > 0 ? 1 : -1; // 이동 방향 결정
        while (currentAngle != targetAngle) {
          currentAngle += step;
          myservo[i].write(currentAngle);
          delay(15); // 움직임 속도 조절 (50 밀리초)
        }
      }
      delay(500);
      for(int i = 80;i> 50;i--){
        myservo[1].write(i);
        delay(10);
      }
      for (int i = 0; i < SERVOS; i++) {
        int targetAngle =firstAngles[i];
        int currentAngle = myservo[i].read();
        int step = (targetAngle - currentAngle) > 0 ? 1 : -1; // 이동 방향 결정
        while (currentAngle != targetAngle) {
        currentAngle += step;
        myservo[i].write(currentAngle);
        delay(15); // 움직임 속도 조절 
        }
      }
      delay(500);
    for (int i = 60; i <= 130; i++){
        myservo[1].write(i); 
        delay(10);
      }
      delay(400);
      for (int i = 40; i <= 80; i++){
        myservo[2].write(i); 
        delay(10);
      }

      switch (input[1]) {
        case 0:
        case 3:
        case 4:
        case 5:
            hand2 =50;
            break;
        case 2:
        case 1:
            hand2 = 60;
            break;
      }
      delay(1000);
      myservo[5].write(hand2);
      delay(500);
      
      for (int i = 120; i >= 60; i--){
        myservo[1].write(i); 
        delay(10);
      }
      delay(1000);
      for (int i = 0; i < SERVOS; i++) {
        int targetAngle = commands[input[1]][i];
        int currentAngle = myservo[i].read();
        int step = (targetAngle - currentAngle) > 0 ? 1 : -1; // 이동 방향 결정
        while (currentAngle != targetAngle) {
          currentAngle += step;
          myservo[i].write(currentAngle);
          delay(15); // 움직임 속도 조절 (50 밀리초)
        }
      }
      delay(500);

      for(int i = 80;i> 50;i--){
        myservo[1].write(i);
        delay(10); 
      }    
      for (int i = 0; i < SERVOS; i++) {
        int targetAngle =firstAngles[i];
        int currentAngle = myservo[i].read();
        int step = (targetAngle - currentAngle) > 0 ? 1 : -1; // 이동 방향 결정
        while (currentAngle != targetAngle) {
        currentAngle += step;
        myservo[i].write(currentAngle);
        delay(15); // 움직임 속도 조절 
        }
      }
      delay(500);
      for (int i = 85; i >= 65; i--){
        myservo[0].write(i); 
        delay(10);
      }
        for (int i = 60; i <= 130; i++){
        myservo[1].write(i); 
        delay(10);
      }
      delay(400);
      for (int i = 40; i <= 80; i++){
        myservo[2].write(i); 
        delay(10);
      }
      
      switch (input[2]) {
        case 0:
        case 3:
        case 4:
        case 5:
            hand3 =50;
            break;
        case 2:
        case 1:
            hand3 = 60;
            break;
      }
      delay(1000);
      myservo[5].write(hand3);
      delay(500);
      
      for (int i = 120; i >= 60; i--){
        myservo[1].write(i); 
        delay(10);
      }
      delay(1000);
      for (int i = 0; i < SERVOS; i++) {
        int targetAngle = commands[input[2]][i];
        int currentAngle = myservo[i].read();
        int step = (targetAngle - currentAngle) > 0 ? 1 : -1; // 이동 방향 결정
        while (currentAngle != targetAngle) {
          currentAngle += step;
          myservo[i].write(currentAngle);
          delay(15); // 움직임 속도 조절 (50 밀리초)
        }
      }
      delay(500);
      for(int i = 80;i> 50;i--){
        myservo[1].write(i);
        delay(10);
      }
      for (int i = 0; i < SERVOS; i++) {
        int targetAngle =firstAngles[i];
        int currentAngle = myservo[i].read();
        int step = (targetAngle - currentAngle) > 0 ? 1 : -1; // 이동 방향 결정
        while (currentAngle != targetAngle) {
        currentAngle += step;
        myservo[i].write(currentAngle);
        delay(15); // 움직임 속도 조절 
        }
      }
      currentindex = 0;
      hand1=0;
      hand2=0;
      hand3=0;
      input[0]=0;
      input[1]=0;
      input[2]=0;
      }
    }
  }
}
    
