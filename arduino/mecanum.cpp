#include <SoftwareSerial.h>
#include <AFMotor.h>

AF_DCMotor motor1(1);
AF_DCMotor motor2(2);
AF_DCMotor motor3(3);
AF_DCMotor motor4(4);

const float DISTANCE_CONVERSION_FACTOR = 1 / 58.00;
const unsigned long SAMPLE_INTERVAL = 100;
const int QUEUE_SIZE = 50;

String bluetooth_message = "";
volatile unsigned long lastSampleTime = 0;

SoftwareSerial bluetooth(A0, A1);
const int Trig = A3;
const int Echo = A2;
volatile float frontDistance;

class CircularQueue
{
private:
    float *queue;
    size_t qSize;
    int count;
    int first;
    int last;

public:
    CircularQueue(size_t t)
    {
        qSize = t;
        queue = new float[t];
        first = 0;
        last = 0;
        count = 0;
    }

    ~CircularQueue()
    {
        delete[] queue;
    }

    void add(float value)
    {
        if (count == qSize)
        {
            first = (first + 1) % qSize;
            count--;
        }

        queue[last] = value;
        last = (last + 1) % qSize;
        count++;
    }

    float *getQueue()
    {
        float *orderedQueue = new float[qSize];
        for (int i = 0; i < count; i++)
        {
            orderedQueue[i] = queue[(first + i) % qSize];
        }
        return orderedQueue;
    }

    int getCount()
    {
        return count;
    }

    void printQueue()
    {
        String queueStr = "[";
        for (int i = 0; i < count; i++)
        {
            queueStr += String(queue[(first + i) % qSize]);
            if (i != count - 1)
            {
                queueStr += ",";
            }
        }
        queueStr = queueStr + "]";
        Serial.println(queueStr);
    }
};

CircularQueue dQueue(QUEUE_SIZE);

void move_release()
{
    motor1.run(RELEASE);
    motor2.run(RELEASE);
    motor3.run(RELEASE);
    motor4.run(RELEASE);
}

void move_forward()
{
    motor1.run(FORWARD);
    motor2.run(FORWARD);
    motor3.run(FORWARD);
    motor4.run(FORWARD);
}

void move_backward()
{
    motor1.run(BACKWARD);
    motor2.run(BACKWARD);
    motor3.run(BACKWARD);
    motor4.run(BACKWARD);
}

void move_left()
{
    motor1.run(BACKWARD);
    motor2.run(FORWARD);
    motor3.run(FORWARD);
    motor4.run(BACKWARD);
}

void move_right()
{
    motor1.run(FORWARD);
    motor2.run(BACKWARD);
    motor3.run(BACKWARD);
    motor4.run(FORWARD);
}

float checkDistance()
{
    digitalWrite(Trig, LOW);
    delayMicroseconds(2);
    digitalWrite(Trig, HIGH);
    delayMicroseconds(10);

    float distance = pulseIn(Echo, HIGH) * DISTANCE_CONVERSION_FACTOR;

    if (distance == 0)
    {
        return -1;
    }

    delay(10);
    return round(distance * 10.0) / 10.0;
}

void processCommand(String command)
{
    command.trim();

    if (command == "forward")
    {
        move_forward();
    }
    else if (command == "backward")
    {
        move_backward();
    }
    else if (command == "left")
    {
        move_left();
    }
    else if (command == "right")
    {
        move_right();
    }
    else if (command == "stop")
    {
        move_release();
    }
}

void setup()
{
    Serial.begin(9600);
    bluetooth.begin(9600);

    pinMode(Echo, INPUT);
    pinMode(Trig, OUTPUT);

    motor1.setSpeed(255);
    motor1.run(RELEASE);
    motor2.setSpeed(255);
    motor2.run(RELEASE);
    motor3.setSpeed(255);
    motor3.run(RELEASE);
    motor4.setSpeed(255);
    motor4.run(RELEASE);
}

void loop()
{
    while (bluetooth.available())
    {
        char c = bluetooth.read();

        if (c == '\n' || c == '\r')
        {
            Serial.println(bluetooth_message);
            processCommand(bluetooth_message);
            bluetooth_message = "";
        }
        else
        {
            bluetooth_message += c;
        }
    }
}