document.addEventListener('DOMContentLoaded', (e)=>{
    $password_input = $('input[name=password]')

    //show password
    $('input[type=checkbox]').click(e=>{
        $e = e.target
        $password_input.attr('type', $e.checked ? 'text' : 'password')
        $('#psw').text( $e.checked ? 'Password encoded' : 'Password decoded')
    })

    // submit form
    $('form').submit(e=>{
        $user_id = $('input[name=user-id]').val()
        $user_tag = $('input[name=user-tag]').val()
        $password = $password_input.val()
        $regex = /^user@ [a-z]+$/

        if ( ! $regex.test($user_tag + $user_id))
            return false
    })
})