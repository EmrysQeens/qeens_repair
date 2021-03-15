templates = {
    'register': {
        'html': """
            <form id="form_reg" method="post">
            {% if not register %}
            <input type="hidden" value="{{repair.id}}" name="id">
            {% endif %}
            <input type="hidden" value="{{ 'register' if register else 'edit_save'}}" name="event">
            <input type="text" name="first_name" class="form-control form-control-sm" placeholder="First Name ??" maxlength="35" autocomplete="off" required value="{{"" if register else customer.first_name}}">
            <input type="text" name="last_name" class="form-control form-control-sm" placeholder="Last Name ??" maxlength="35" autocomplete="off" required value="{{"" if register else customer.last_name}}">
            <input type="file"name="image" accept="image/*" class="form-control form-control-sm">
            <input type="number" name="mobile_number" class="form-control form-control-sm" placeholder="Mobile Number ??" maxlength="11" minlength="11" required autocomplete="off" value="{{"" if register else mobile_number}}">
            <div style="padding-left: 22px;">
                {% for manufacturer in manufacturers %}
                    <div class='mn'>
                        <input class="form-check-input" type="radio" required name="manufacturer" value="{{ manufacturer.name }}"  {{ '' if register else 'checked' if manufacturer.name == manufacturer_.name  else '' }}>
                        <span class="spn">{{ manufacturer.name }}</span>
                    </div>
                {% endfor %}
            </div>
            <input type="text" required name="model" class="form-control form-control-sm" maxlength="25" placeholder="Model Number ??" autocomplete="off" value="{{"" if register else repair.model }}">
            <input type="number" name="imei" class="form-control form-control-sm" placeholder="Imei ??" maxlength="15" autocomplete="off" value="{{"" if register else "" if imei is none else imei.imei }}">
            <input type="text" name="device_pass" class="form-control form-control-sm" maxlength="30" placeholder="Device Passcode ??" autocomplete="off" value="{{"" if register else repair.device_pass }}">
            <input type="text" name="fault" class="form-control form-control-sm" maxlength="255" placeholder="Device Fault ??" autocomplete="off" value="{{"" if register else repair.fault }}">
            <input type="text" name="battery_serial_no" class="form-control form-control-sm" maxlength="50" placeholder="Battery Serial Number ??" autocomplete="off" value="{{"" if register else repair.battery_serial_no }}">
            <input type="text" name="accessories_collected" class="form-control form-control-sm" placeholder="Accessories collected ??" autocomplete="off" value="{{"" if register else repair.accessories_collected }}">
            <input type="number" name="cost" class="form-control form-control-sm" placeholder="Cost ??" autocomplete="off" value="{{"" if register else repair.cost}}">
            <input type="number" name="paid" class="form-control form-control-sm" placeholder="Paid ??" autocomplete="off" value="{{"" if register else repair.paid}}">
            <button type="submit" class="btn btn-sm" id="register_btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-upload" viewBox="0 0 16 16">
                  <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                  <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
                </svg>
            </button>
     </form>
        """,
        'js': """
            $nm_test = /^[a-zA-Z]{1,35}$/
            $device_test = /^(pi|pa)(n:\d{4,}|ttern:\d{5,9}|ssword:.{4,})$/ //^(pin:[0-9]{4,}|pattern:[0-9]{5,9}|password:.+)$/
            $digit_test = /^(\d{11}|\d{15})$/
            $first_name = $('input[name=first_name]')
            $last_name = $('input[name=last_name]')
            $mobile_number = $('input[name=mobile_number]')
            $imei = $('input[name=imei]')
            $device_pass = $('input[name=device_pass]')
            $image = document.querySelector('input[name=image]')    //todo
    
            $('#form_reg').submit( async (e)=>{
                e.preventDefault()
                if ( !$nm_test.test($first_name.val()) ||  !$nm_test.test($last_name.val()) || !$digit_test.test($mobile_number.val()))
                    return
                $ps_code = $device_pass.val()
                $imei_code = $imei.val()
                if ($ps_code !='' && !$device_test.test($ps_code))
                    return
                if ($imei_code !='' && !$digit_test.test($imei_code))
                    return
    
                $data = {'image':'', 'date_b': new Date().toUTCString()}
    
                if ($image.files.length>0){
                    $image_data = await toBase64($image.files[0])
                    if (! $image_data[1]) return
                    $data['image'] = $image_data[0]
                }
    
                $form_datas = $('#form_reg').serialize().split("&")
                for ($form_data of $form_datas){
                    $cur = $form_data.split("=")
                    $data[$cur[0]] = $cur[1]
                }
    
                if ($data['manufacturer'] === undefined) {
                    alert('Manufacturer not selected.')
                    return
                }

                $req = new Requests($end_pt_url,'POST', $data)
    
                $req.success( (data, stat, status)=>{
                    $stat = data['stat']
                    if (stat==='success'){
                        if ( $stat === 'ok') {
                            console.log($stat)
                            $container.html(templates['register']['html'])
                            eval(templates['register']['js'])
                            $('input[name=event]').val('register')
                            alert('Success')
                            }
                        else if( $stat === 'mobile_err') alert(`Mobile number maps to a ${data['name']} already`)
                        else if( $stat === 'amount_err') alert('Why is paid greater than cost') 
                        else if( $stat === 'no_customer') alert (`Customer with this mobile number doesn't exist. Register don't edit`)
                    }
                })
    
                $req.failed( stat_text=> alert(stat_text))
                return false
            })
        """,
    },

    'search': {
        'html': """
            <div class="cent s_cent_o" id="search_cent">
                <input type="text" name="query" class="inline form-control form-control-sm" placeholder="type: query " autocomplete="off" minlength="" maxlength="30" required style="width: 80%;">
                <button id="btn_search" class="btn" style="padding-top: 12px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-search" viewBox="0 0 16 16">
                            <path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z"/>
                    </svg>
                </button>
                <p class="spn">You can search via mobile number or imei.</p>
                <p class="spn">type:query</p>
                <p class="spn">your search pattern should follow the above syntax.</p>
                <p class="spn">for imei type  = imei and query = value. ( imei:356478673456524)</p>
                <p class="spn">for mobile number type = mobile query = value. ( mobile:09091322470)</p>
            </div>
            <div id="result" style="display: none;">
                
            </div>
        """,
        'js': """
            $btn_search = $('#btn_search')
            $query = $('input[name=query]')
            $search_cent = $('#search_cent')
            $bool = false


            $query.focus(e=>{
                if ($bool){
                    $('#result').css('display', 'none')
                    $('#result').html('')
                    $search_cent.css('animation-name','trans_down')
                    $search_cent.css('animation-play-state','running')
                    document.querySelector('#search_cent').onanimationend=e=>{ //todo jquery on end
                        $bool = false
                        $btn_search.attr('disabled', $bool)
                       }
                    }
            })

            $btn_search.click(e=>{
                if (! /^(imei:[0-9]{15}|mobile:[0-9]{11})$/.test($query.val())){
                    alert('Invalid query in search box.')
                    return
                }
                if($bool) return


                 $req = new Requests($end_pt_url, "POST", {'event':'search', 'query': $query.val(), 'pos': 0})
                 $req.success( (data, stat, status) => {
                     if (stat === 'success'){
                        stat_ = data['stat']
                        if (stat === 'err') alert('Invalid query in search box.')
                        else if (stat_ === 'repair' || stat_ ==='customer') {
                            if (!$bool) {
                                $search_cent.css('animation-name','trans_up')
                                $search_cent.css('animation-play-state','running')
                            }
                            document.querySelector('#search_cent').onanimationend=e=>{ //todo jquery on end
                                $bool=true
                                $('#result').html(data['html'])
                                $('#result').css('display', 'block')
                                eval(data['js'])
                                $btn_search.attr('disabled', $bool)
                            }
                        }
                        else alert (`Repair with ${stat_ === 'no_repair' ?  'imei' : 'mobile number'} does not exist`)
                     }
                 })
                 $req.failed( stat_text=> alert(stat_text))
            })
        """,
    },

    'view': {
        'html': """
        <div style="max-width: 300px; margin: auto;" >
            <input type='hidden' name='repair_pos' value='{{pos}}'>
            <input type='hidden' name='repair_id' value='{{repair.id}}'>
            <img src="{{ image if customer.image=='' else customer.image }}" alt="image" width="250px" height="250px" style="border-radius: 5px; padding-bottom: 20px;">
            <p class="r_p">Name : {{ customer.first_name+' '+customer.last_name }}</p>
            <p class="r_p">Mobile number : 0{{ customer.mobile_number }}
            <button class='btn' style='display:inline;'>
                <a href='tel:0{{customer.mobile_number}}'>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-telephone-fill" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M1.885.511a1.745 1.745 0 0 1 2.61.163L6.29 2.98c.329.423.445.974.315 1.494l-.547 2.19a.678.678 0 0 0 .178.643l2.457 2.457a.678.678 0 0 0 .644.178l2.189-.547a1.745 1.745 0 0 1 1.494.315l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.634 18.634 0 0 1-7.01-4.42 18.634 18.634 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877L1.885.511z"/>
                    </svg>
                </a>
            </button>
            </p>
            <p class="r_p">Manufacturer : {{ manufacturer.name }}</p>
            <p class="r_p">Model : {{ repair.model }}</p>
            <p class="r_p">Imei : {{ 'null' if repair.imei == "" else imei.imei }}</p>
            <p class="r_p">Passcode : {{ 'null' if repair.device_pass == '' else repair.pass }}</p>
            <p class="r_p">Fault : {{ 'null' if repair.fault == '' else repair.fault }}</p>
            <p class="r_p">Battery Serial No : {{ 'null' if repair.battery_serial_no == '' else repair.battery_serial_no }}</p>
            <p class="r_p">Accessories : {{ 'null' if repair.accessories_collected == '' else repair.accessories_collected }}</p>
            <p class="r_p">Cost : {{ 'null' if repair.cost == 0 else repair.cost }}</p>
            <p class="r_p">Paid : {{ 'null' if repair.paid == 0 else repair.paid }}</p>
            <p class="r_p">Balance : {{ 'null' if repair.balance == 0 else repair.balance }}</p>
            <p class="r_p">Brought : {{ repair.date_b }}</p>
            <p class="r_p">Delivered : {{ 'null' if repair.date_c == '' else repair.date_c }}</p>
            <p class="r_p">Registerer: {{ User.query.get(repair.registerer).username }}</p>
            {% if repair.date_c != '' %}
                <p class="r_p">Deliverer: {{ User.query.get(repair.deliverer).username }}</p>
            {% endif %}
            <input type="checkbox" id="delivered" style="margin: 5px;" {{ "" if repair.date_c == '' else "checked" }} ><span class="spn">Delivered</span></div>
            <div id="controls">
                <button class='btn' id='edit'>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pen-fill" viewBox="0 0 16 16">
                        <path d="M13.498.795l.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001z"/>
                    </svg>
                </button>
                {% if user.is_super_user %}
                <button class='btn' id='delete'>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">
                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                        <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4L4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                    </svg>
                </button>
                {% endif %}
                {% if len > 1 %}
                    <button class="btn" id="prev" {{ 'disabled' if pos == 0 else '' }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-left" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.6479 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z"/>
                        </svg>
                    </button>
                    <button class="btn" id="next" style="float: right;" {{ 'disabled' if (pos == len-1) else '' }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-right" viewBox="0 0 16 16">
                          <path  fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/>
                        </svg>
                    </button>
                {% endif %}
            </div>
        </div>""",
        'js': """
            $.fn.page = pos =>{
                    $data = {'event': 'search', 'query': $('input[name=query]').val(), 'pos': pos }
                    $req = new Requests($end_pt_url, 'POST', $data)
                    $req.success((data, stat, status)=>{
                        $stat_ = data['stat']
                        if (stat === 'success' && stat_ != 'err') {
                            $('#result').html(data['html'])
                             eval(data['js'])
                        }
                    })
                    $req.failed(stat_text => alert(stat_text))
                    }
                
                
                $('#delivered').click(e => {
                    checked = e.target.checked
                    e.target.checked = checked
                    $data = {
                                    'event': 'deliver', 'checked': checked,
                                    'id': $('input[name=repair_id]').val(),
                                     'date_c': new Date().toUTCString()
                                     }
                     console.log($data['checked'])
                    $req = new Requests($end_pt_url, 'POST', $data)
                    $req.success((data, stat, status)=>{
                        if (stat === 'success' && data['stat']) {
                            alert('Delivered')
                            $.fn.page($('input[name=repair_pos]').val())
                        }
                    })
                    $req.failed(stat_text=>{
                        e.target.checked = ! checked
                        alert(stat_text)
                    })
                
                })
                
                
                $('#delete').click(e=>{
                    $data = {
                                    'event': 'delete',
                                    'id': $('input[name=repair_id]').val(),
                                    }
                    $req = new Requests($end_pt_url, 'POST', $data)
                    $req.success((data, stat, status)=>{
                        $stat_ = data['stat']
                        if(stat === 'success' &&  $stat_ === 'ok') alert('Repair Deleted')
                        else alert('No Repair')
                        $('input[name=query]').focus()
                    })
                    $req.failed(stat_text => alert(stat_text))
                })
                
                
                $('#edit').click(e=>{
                    $data = {'event': 'edit', 'id': $('input[name=repair_id]').val(), }
                    $req = new Requests($end_pt_url, 'POST', $data)
                    $req.success((data, stat, status)=>{
                        $stat_ = data['stat']
                        if (stat === 'success' && $stat_) {
                            $('#layout').html(data['html']) // todo
                            eval(data['js'])
                        }
                        else alert('Repair does not exist.')
                    })
                    $req.failed(stat_text => alert(stat_text))
                
                })
                
                $.fn.control = e =>{
                    e.click(e=>{
                        $po = Number($('input[name=repair_pos]').val())
                        $pos = e.currentTarget.id === 'next' ? $po + 1 : $po - 1
                        $.fn.page($pos)
                    })
                }
                
                $.each([$('#prev'), $('#next')], (i,e)=> $.fn.control(e))

        """},

    'welcome': {
        'html': """
            <div style="text-align: center;">
                <img id='user_img' src="{{ image if user.image== ''  else user.image }}" alt="image" width="200px" height="200px" style="border-radius: 5px; padding-bottom: 20px;">
            </div>
            <div class="cent" id="welcome_div">
                <h3> Welcome @ <span class="spn">{{ user.username }}</span></h3>
                <span class="spn">Today is a good day {{ username }}. Have faith and all will be well.</span>
                <p class="spn">Stay Blessed</p>
                <p id="welcome_msg_1" class="spn"></p>
                {% if user.is_super_user %}
                <button class="btn inline" id="user_new">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-plus" viewBox="0 0 16 16">
                        <path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0zm4 8c0 1-1 1-1 1H1s-1 0-1-1 1-4 6-4 6 3 6 4zm-1-.004c-.001-.246-.154-.986-.832-1.664C9.516 10.68 8.289 10 6 10c-2.29 0-3.516.68-4.168 1.332-.678.678-.83 1.418-.832 1.664h10z"/>
                        <path fill-rule="evenodd" d="M13.5 5a.5.5 0 0 1 .5.5V7h1.5a.5.5 0 0 1 0 1H14v1.5a.5.5 0 0 1-1 0V8h-1.5a.5.5 0 0 1 0-1H13V5.5a.5.5 0 0 1 .5-.5z"/>
                    </svg>
                </button>
                {% endif %}
                <button class="btn inline" id="user_edit">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pen-fill" viewBox="0 0 16 16">
                        <path d="M13.498.795l.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001z"/>
                    </svg>
                    <span class='spn'> Edit your account</span>
                </button>
            </div>
        """,
        'js': """
             $loader.css('display', 'none')
             $welcome_cent = $('#welcome_div').html()
             $btns = [$('#user_new'), $('#user_edit')]
             $.each($btns, (i,e)=>{
                e.click(e=>{
                    $req = new Requests($end_pt_url, 'POST', {'event' : 'user', 'id' :  e.currentTarget.id})
                    $req.success((data, stat, status)=>{
                        if(stat === 'success'){
                            $('#welcome_div').html(data['html'])
                            eval(data['js'])
                            }
                    })
                    $req.failed(stat_text => alert(stat_text))
                })
             })
             $.fn.print("I have not failed. I've just found 10,000 ways that won't work. Failure is not the opposite of success it's a part of success.You build on failure. You use it as a stepping stone. Close the door on the past. You don't try to forget the mistakes, but you don't dwell on it. You don't let it have any of your energy, or any of your time, or any of your space.  Qeens_Inc.", 50, $('#welcome_msg_1'), e=>{})
        """,
    },

    'user': {
        'html': """
            <form id="form_user" method="post">
            <input type="hidden" name="action" value="{{ "user_new" if new else 'user_edit' }}">
            <input type="hidden" name="event" value="sv_usr">
              <div class="row">
                <div class="col">
                  <input type="text" class="form-control form-control-sm" name="username" placeholder="Username" required value="{{'' if new else user.username}}">
                </div>
                <div class="col">
                  <input type="email" class="form-control form-control-sm" name="email" placeholder="E-Mail" required value="{{"" if new else user.email}}">
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <input type="file" name="user_image" class="form-control form-control-sm" accept="image/*" class="form-control sm">
                </div>
                {% if user.is_super_user or new %}
                <div class="col">
                  <div class="form-check form-check-inline">
                  <input class="form-check-input" type="checkbox" name="super_user" {{ "" if new or not user.is_super_user else "checked"}}>
                  <label class="spn" for="super_user">Super User: A super user can add a user, delete a repair, e.t.c</label>
                </div>
                {% endif %}
                </div>
              </div>
              <input type="password" name="password_user" class="form-control form-control-sm" placeholder="Password" required>
              <div class="form-check form-check-inline">
                  <input class="form-check-input" type="checkbox" id="user_psw_v">
                  <label class="spn" for="user" id="p_en">Password encoded</label>
                </div>
                <button type="submit" class="btn btn-sm" id="user_action">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-upload" viewBox="0 0 16 16">
                        <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                        <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
                    </svg>
                </button>
            </form>
        """,
        'js': """
            $('#user_psw_v').click(e=> $.fn.show_psw(e, $('input[name=password_user]'), x=> $('#p_en').text( x.checked ? 'Password encoded' : 'Password decoded') ))
            $image_  = document.querySelector('input[name=user_image]')
            if ($('input[name=action]').val() === 'user_edit'){
                $image_.onchange = async (e)=>{
                    if ($image_.files.length>0){
                        $image_data = await toBase64($image_.files[0])
                        if (! $image_data[1]) return
                        $('#user_img').prop('src', $image_data[0])
                    }
                }
                }
            $('#form_user').submit( async (e)=>{
                e.preventDefault()
                $data = {'image' : ""}
                $form_datas = $('#form_user').serialize().split("&")
                for ($form_data of $form_datas){
                    $cur = $form_data.split("=")
                    $data[$cur[0]] = $cur[1]
                }
                $data['email'] = $('input[name=email]').val()
                if ($image_.files.length>0){
                    $image_data = await toBase64($image_.files[0])
                    if (! $image_data[1]) return
                    $data['image'] = $image_data[0]
                }
                $data['super_user'] = $('input[name=super_user]').prop('checked')
                $req = new Requests($end_pt_url,'POST', $data)
                $req.success( (data, stat, status)=>{
                    $stat = data['stat']
                    $action = data['action']
                    if (stat==='success'){
                        if ( $stat === 'updated' && $action === 'user_edit') alert('Success.. Details saved.')
                        else if( $stat === 'created' && $action === 'user_new') alert('Success.. User created')
                        else alert( 'Password Incorrect')
                        if ($stat != 'err')  {
                            $('#welcome_div').html($welcome_cent)
                            eval(templates['welcome']['js'])
                            }
                    }
                })
    
                $req.failed( stat_text=>  alert(stat_text))
                return false
            })
        """,
    },

    'login': """
            <div class="cent">
                <h3>Qeens_Inc</h3>
                <form method="POST" action="/">
                     <input type="text" name="user-tag" value="user@ " class="form-control form-control-sm in" style="width:20.5%;" readonly>
                    <input type="text" name="user-id" name="username" class="form-control form-control-sm in"  style="width: auto;" placeholder="User ID ??" required autocomplete="off">
                    <input type="password" name="password" class="form-control form-control-sm" placeholder="Password ??" autocomplete="no"required>
                    <input type="checkbox" class="form-check-input" style="margin-left: 0; position: relative;">
                    <span class="psw" id="psw">Password decoded</span>
                    <button class="btn right" type="submit">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 14 14" width="16" height="16"><path fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"></path></svg>
                    </button>
                </form>
        </div>
    """,
}

