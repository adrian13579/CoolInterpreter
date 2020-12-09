(* This program prints the first 10 numbers of fibonacci *)
class Main {

    main(): Object {
        let total: AUTO_TYPE <- 10,
            i: AUTO_TYPE <- 1 ,
            io: AUTO_TYPE <- new IO in
                while i < total loop {
                    io.out_int(bonacci(i));
                    io.out_string("\n");
                    i <- i + 1;
                }
                pool
    };

    bonacci (n: AUTO_TYPE): AUTO_TYPE {
       if n < 2 then 1 else bonacci(n - 1) + bonacci(n - 2) fi
   };
};