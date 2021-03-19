document.addEventListener('DOMContentLoaded', (e)=>{
//
//    $.fn.switch_ = (bool) => {
//        if (bool){
//            $loader.css('display', 'none')
//            $container.css('display', 'block')
//            return
//        }
//        $container.css('display', 'none')
//        $loader.css('display', 'block')
//    }

    $.fn.switch_ = (bool) => {
        if (bool){
            $loader.css('display', 'none')
            //$container.css('display', 'block')
            return
        }
        //$container.css('display', 'none')
        $loader.css('display', 'block')
    }


    // Request class.
    Requests = function(url_, method_type, data){
        $r =  $.ajax({
                url: url_,
                method: method_type,
                data: data,
                beforeSend: ()=> $.fn.switch_(false),
                timeout: 120000
         })
    }

    // extending request features.
    $.extend(Requests.prototype, {
        success: (ext)=>{
            $r.done((data, stat) => {
                $.fn.switch_(true)
                ext(data, stat, $r.status)
            })
        },

        info: ()=> {
            return {
                'status': $r.status,
                'state': $r.readyState,
                'response': $r.responseText,
                'status_text': $r.statusText,
                'state': $r.state()
            }
        },

        failed: (ext)=>{
            $r.fail(()=>{
                $.fn.switch_(true)
                ext($r.statusText)
            })
        },

        get: ()=> $r

    })

})