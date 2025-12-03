import './Button.css' 

function Button( {Value , name, onClick, disabled} ){
  
return(
  <>
    <button className={name} onClick={onClick} disabled={disabled} >
      {Value}
    </button>

  </>
)

}

export default Button