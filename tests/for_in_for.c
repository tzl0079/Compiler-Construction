int main() {
    int x = 0;

    for(int i = 0; i < 10; i++)
    {
        for(int j = 2; j < 8; j++)
        {
            if (j % 2 == 0) {
                x += 2;
            }
        }
    }
}