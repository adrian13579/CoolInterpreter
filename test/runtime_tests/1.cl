class Main {
    a :Fact ;
    main(): Int {{
        a <- new Ackermann;
        a.ackermann(2,3);
        }
    };
};

class Fact {
    fact(n : Int): Int{
        if (n=0) then 1 else n*fact(n-1) fi
    };
};

class Ackermann {
    ackermann(m:Int, n: Int): Int{
        if (m = 0 ) then n+1 else
            if ( n = 0) then ackermann(m-1, 1) else
                ackermann(m-1, ackermann(m, n-1))
            fi
        fi
    };
};