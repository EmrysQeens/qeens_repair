document.addEventListener('DOMContentLoaded', function(e){
    $username = undefined
    $active_btn = undefined
    // radio btns
    $register = $('#register')
    $welcome = $('#welcome')
    $search = $('#search')
    templates = {
        'search' : {
            'html': undefined,
            'js': undefined,
        },
        'register' : {
            'html': undefined,
            'js': undefined,
        },
        'welcome': {
            'html': undefined,
            'js': undefined,
        }
    }

    $loader = $('#loader')
    $container = $('#layout')
    $end_pt_url = 'event'

    $.fn.print = function (text, interval, elem, func){
        $counter = 0    // defines start of printed text.
        $interval = setInterval( function(){   // start printing text
            elem.text(text.substring(0, ++$counter))    // set text from substring ( 0 to counter where counter increases by one every 100ms)
            if ( $counter === text.length ) {   // if whole text is printed.
                clearInterval($interval)    // stop printing.
                func($counter)  // returns counter in a callback if needed anywhere in function call
            }
        }, interval)
     }

     const toBase64 = function(file){ return new Promise(function(resolve, reject){
                const reader = new FileReader()
                if (file == undefined) return
                reader.readAsDataURL(file)
                reader.onload = function(){resolve([reader.result, true])}
                reader.onerror = function(err){ reject([err, false])}
     })
     }

     const to_b64 = function(file, resolve){
                const reader = new FileReader()
                if (file == undefined) return
                reader.readAsDataURL(file)
                reader.onload = function(){resolve(reader.result, true)}
                reader.onerror = function(err){ alert('image decoding error.')}
     }

    //  logout button click event listener.
    $('#logout').click( function (){
        $req = new Requests($end_pt_url, 'POST', {'event': 'logout'})
        $req.success( function (data, stat, staus){
            if ( stat === 'success'){
                document.write(data)
                document.close()
                document.title = 'Login'
                window.history.replaceState('', 'Login', '/login')
                window.location.href = window.location.href
                }
        })
        $req.failed(function(stat_text){
            alert(stat_text)    //todo
        })
    })


    $.fn.re = function(e){
        id = e.target.id
        //if (e.target.checked)   return
        if (templates[id]['html'] != undefined){
            $container.html(templates[id]['html'])
            eval(templates[id]['js'])
            return
        }
        $req = new Requests($end_pt_url, 'POST', {'event': 'template', 'template': id})
        $req.success( function(data, stat, status){
            if ( stat === 'success'){
                html = data['html']
                js = data['js']
                $container.html(html)
                eval(js)
                templates[id]['js'] = js
                templates[id]['html'] = html
              }
        })
        $req.failed( function(stat_text){
            alert(stat_text)    //todo
        })
    }

    $.each([$register, $search, $welcome], function(i,e){e.click(function(e) {$.fn.re(e)})})

    // Add manufacturer
    $manufacturer = $('input[name=manufacturer]')
    $('#form_manu').submit( function (e){
        e.preventDefault()
        $active_menu_btn = $('#menu * input[type=radio]:checked')
        $manufacturer_ = $manufacturer.val()
        if ($manufacturer_ === "")
            return
        $data = {
            'event': 'manufacturer', 'manufacturer': $manufacturer_,
        }

        $req = new Requests($end_pt_url,'POST', $data)
        $.fn.template = function(){
            $count = 0
            $r_ = new Requests($end_pt_url, 'POST', {'event': 'template', 'template': 'register'})
            $r_.success(function(data, stat, status){
                html = data['html']
                templates['register']['html'] = html
                eval(templates['register']['js'])
                $active_menu_btn.click()
                $manufacturer.val('')
             })
             $r_.failed(function(stat_text){
                if (stat_text != 'timeout'){
                    alert('Reload page to reflect')
                    return
                }
                if ($count++ < 5)
                    $.fn.template()
                else alert('Reload page to reflect')
             })
        }
        $req.success( function(data, stat, status){
           if (stat==='success'){
             $.fn.template()
             if (data['stat']) alert('Success')
             else alert('Manufacturer exists.')
           }
        })

         $req.failed( function(stat_text){alert(stat_text)})
        })


    $.fn.show_psw = function(e, input, func){
        $e = e.target
        input.attr('type', $e.checked ? 'text' : 'password')
        func($e)
    }

    //show password
    $psw_inp = [$('input[name=old_psw'), $('input[name=new_psw')]
    $.each([$('#old_psw_chk'), $('#new_psw_chk')], function(i, e){
        e.click(function(e){$.fn.show_psw(e, $psw_inp[i], function(x){})})
    })

        $('#form_psw').submit( function(e){
            e.preventDefault()
            $data = {'event': 'change_psw', 'psw_old': $psw_inp[0].val(), 'psw_new': $psw_inp[1].val()}
            $req = new Requests($end_pt_url, 'POST', $data)
            $req.success(function(data, stat, status){
                $stat_ = data['stat']
                if (stat === 'success'){
                        $.each($psw_inp, function(i,e){e.val('')})
                        if($stat_ === 'psw_err') alert('Wrong old password.')
                        else alert('Password Successfully changed.')
                }
            })

            $req.failed( function(stat_text){alert(stat_text)})
        })

    $welcome.click()

})
