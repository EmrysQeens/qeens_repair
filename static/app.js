document.addEventListener('DOMContentLoaded', (e)=>{
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

    $.fn.print = (text, interval, elem, func)=>{
        $counter = 0    // defines start of printed text.
        $interval = setInterval(()=>{   // start printing text
            elem.text(text.substring(0, ++$counter))    // set text from substring ( 0 to counter where counter increases by one every 100ms)
            if ( $counter === text.length ) {   // if whole text is printed.
                clearInterval($interval)    // stop printing.
                func($counter)  // returns counter in a callback if needed anywhere in function call
            }
        }, interval)
     }

     const toBase64 = file => new Promise((resolve, reject)=>{
                const reader = new FileReader()
                if (file == undefined) return
                reader.readAsDataURL(file)
                reader.onload = () => resolve([reader.result, true])
                reader.onerror = (err) => reject([err, false])
     })

    //  logout button click event listener.
    $('#logout').click(() => {
        $req = new Requests($end_pt_url, 'POST', {'event': 'logout'})
        $req.success((data, stat, staus)=>{
            if ( stat === 'success'){
                document.write(data)
                document.close()
                document.title = 'Login'
                window.history.replaceState('', 'Login', '/login')
                window.location.href = window.location.href
                }
        })
        $req.failed(stat_text=>{
            alert(stat_text)    //todo
        })
    })


    $.fn.re = (e) => {
        id = e.target.id
        //if (e.target.checked)   return
        if (templates[id]['html'] != undefined){
            $container.html(templates[id]['html'])
            eval(templates[id]['js'])
            return
        }
        $req = new Requests($end_pt_url, 'POST', {'event': 'template', 'template': id})
        $req.success( async (data, stat, status)=>{
            if ( stat === 'success'){
                html = data['html']
                js = data['js']
                await $container.html(html)
                eval(js)
                templates[id]['js'] = js
                templates[id]['html'] = html
              }
        })
        $req.failed(stat_text=>{
            alert(stat_text)    //todo
        })
    }

    $.each([$register, $search, $welcome], (i,e)=>e.click(e=> $.fn.re(e)))

    // Add manufacturer
    $manufacturer = $('input[name=manufacturer]')
    $('#form_manu').submit( async (e)=>{
        e.preventDefault()
        $active_menu_btn = $('#menu * input[type=radio]:checked')
        $manufacturer_ = $manufacturer.val()
        if ($manufacturer_ === "")
            return
        $data = {
            'event': 'manufacturer', 'manufacturer': $manufacturer_,
        }

        $req = new Requests($end_pt_url,'POST', $data)
        $.fn.template = () =>{
            $count = 0
            $r_ = new Requests($end_pt_url, 'POST', {'event': 'template', 'template': 'register'})
            $r_.success((data, stat, status)=>{
                html = data['html']
                templates['register']['html'] = html
                $active_menu_btn.click()
                $manufacturer.val('')
             })
             $r_.failed(stat_text=> {
                if (stat_text != 'timeout'){
                    alert('Reload page to reflect')
                    return
                }
                if ($count++ < 5)
                    $.fn.template()
                else alert('Reload page to reflect')
             })
        }
        $req.success( (data, stat, status)=>{
           if (stat==='success'){
             $.fn.template()
             if (data['stat']) alert('Success')
             else alert('Manufacturer exists.')
           }
        })

         $req.failed( stat_text => alert(stat_text))
        })


    $.fn.show_psw = (e, input, func) =>{
        $e = e.target
        input.attr('type', $e.checked ? 'text' : 'password')
        func($e)
    }

    //show password
    $psw_inp = [$('input[name=old_psw'), $('input[name=new_psw')]
    $.each([$('#old_psw_chk'), $('#new_psw_chk')], (i, e)=>{
        e.click(e=>$.fn.show_psw(e, $psw_inp[i], x=>{}))
    })

        $('#form_psw').submit( e=>{
            e.preventDefault()
            $data = {'event': 'change_psw', 'psw_old': $psw_inp[0].val(), 'psw_new': $psw_inp[1].val()}
            $req = new Requests($end_pt_url, 'POST', $data)
            $req.success((data, stat, status)=>{
                $stat_ = data['stat']
                if (stat === 'success'){
                        $.each($psw_inp, (i,e)=>e.val(''))
                        if($stat_ === 'psw_err') alert('Wrong old password.')
                        else alert('Password Successfully changed.')
                }
            })

            $req.failed( stat_text => alert(stat_text))
        })

    $welcome.click()

})
