class Main {
    x: AUTO_TYPE;

    main (): AUTO_TYPE {
        x <- new A
     };
    succ(n : AUTO_TYPE) : AUTO_TYPE { n + 1 };
};

class A inherits IO {
    methodA(): AUTO_TYPE {
        out_string("Hola")
    };
};

