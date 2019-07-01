#include <functional>
#include <iostream>

std::function<int(int, int)> returnLambda(){
    return [] (int x, int y){
        return x*y;
    };
}


int main(){

    int x = 0;
    int y = 42;
    auto qqq = [x, &y] {
        std::cout << "x: " << x << std::endl;
        std::cout << "y: " << y << std::endl;
        ++y;
    };
    qqq();
    qqq();
    std::cout << "final y: " << y << std::endl;
    
    auto lf = returnLambda();
    std::cout << lf(6, 7) << std::endl;
}