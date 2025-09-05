import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateModelsComponent } from './create-models.component';

describe('CreateModelsComponent', () => {
  let component: CreateModelsComponent;
  let fixture: ComponentFixture<CreateModelsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CreateModelsComponent]
    });
    fixture = TestBed.createComponent(CreateModelsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
