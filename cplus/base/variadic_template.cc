#include <cstdlib>
#include <iostream>
#include <bitset>
#include <vector>
#include <algorithm>
#include <map>
#include <string>

void print(){

}

template<typename T, typename... Types>
void print(const T& firstArg, const Types&... args){
    std::cout << firstArg << std::endl;
    print(args...);
}

void print_sqrt(int a){
    std::cout << 2*a << std::endl;
}

template <typename T>
using Vec = std::vector<T>;

int main(){
    print(7.5, "hello", std::bitset<16>(377), 42);
    Vec<int> collect;
    collect.push_back(1);
    collect.push_back(2);
    collect.push_back(3);
    for(auto i : collect){
        std::cout << i << std::endl;
    }

    std::map<std::string , float> coll;
    decltype(coll)::value_type elem;
    
}